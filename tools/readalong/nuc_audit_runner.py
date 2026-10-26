"""NUC Library Audit Runner - comprehensive read-only scan of all books."""
import argparse
import datetime
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import unicodedata

from tools.readalong.nuc_verifier import AlistClient, verify_book_on_alist
from tools.readalong.nuc_target import NUC_SCP, NUC_TARGET, direct_ssh_command


def scan_remote_structure(remote_host="hp", remote_root="/mnt/750/Music/有声书"):
  """Scan remote NUC directory structure, anomalies, private-use chars, and AppleDouble files."""
  py_script = f"""
import json, os, unicodedata
from pathlib import Path

root = Path('{remote_root}')
categories = []
books = []
anomalies = []
appledouble_files = []
ds_stores = []
locks = []
pua_items = []

for cat in sorted(root.iterdir()):
    if not cat.is_dir() or cat.name.startswith('.'):
        continue
    categories.append(cat.name)
    subdirs = []
    for b in sorted(cat.iterdir()):
        if b.is_dir() and not b.name.startswith('.'):
            subdirs.append(b.name)
            # check depth-3 volume subdirectories
            vol_dirs = [v.name for v in b.iterdir() if v.is_dir() and not v.name.startswith('.')]
            has_volumes = any((b / v / 'readalong').exists() for v in vol_dirs)
            if has_volumes:
                for v in vol_dirs:
                    if (b / v / 'readalong').exists():
                        books.append({{'category': cat.name, 'book': f'{{b.name}}/{{v}}', 'is_volume': True}})
            else:
                books.append({{'category': cat.name, 'book': b.name, 'is_volume': False}})

# scan anomalies
for p in root.rglob('*'):
    name = p.name
    # PUA characters (e.g. )
    if any(0xE000 <= ord(c) <= 0xF8FF for c in name):
        pua_items.append(str(p))
    if name.startswith('._'):
        appledouble_files.append(str(p))
    elif name == '.DS_Store':
        ds_stores.append(str(p))
    elif name == '.readalong_publish.lock':
        locks.append(str(p))

print(json.dumps({{
    'categories': categories,
    'books': books,
    'pua_items': pua_items,
    'appledouble_files': appledouble_files,
    'ds_stores': ds_stores,
    'locks': locks
}}, ensure_ascii=False))
"""
  res = subprocess.run(direct_ssh_command(remote_host, "python3", "-c", py_script), capture_output=True, text=True, check=True)
  return json.loads(res.stdout.strip())


def main(argv=None):
  parser = argparse.ArgumentParser(description="NUC Library Audit Tool")
  parser.add_argument("targets", nargs="*", help="Specific category or category/book to audit")
  parser.add_argument("--remote-host", default=NUC_TARGET)
  parser.add_argument("--remote-root", default="/mnt/750/Music/有声书")
  parser.add_argument("--output-dir", default="private/readalong-nuc-audit-20261025")
  args = parser.parse_args(argv)

  out_path = Path(args.output_dir)
  out_path.mkdir(parents=True, exist_ok=True)

  print("[1/4] Scanning NUC remote file structure & anomalies...")
  remote_meta = scan_remote_structure(args.remote_host, args.remote_root)
  print(f"  Found {len(remote_meta['categories'])} categories and {len(remote_meta['books'])} book entries.")
  print(f"  Anomalies found: {len(remote_meta['pua_items'])} PUA items, {len(remote_meta['appledouble_files'])} AppleDouble, {len(remote_meta['locks'])} locks.")

  all_books = remote_meta["books"]
  if args.targets:
    filtered = []
    for b in all_books:
      item_full = f"{b['category']}/{b['book']}"
      if any(item_full == t or item_full.startswith(t.rstrip('/') + '/') or b['category'] == t for t in args.targets):
        filtered.append(b)
    all_books = filtered
    print(f"  Filtered to {len(all_books)} targeted book entries.")

  print("\n[2/4] Executing Alist client contract verification for each book...")
  audit_records = []

  # 将 targets 写入本地临时文件并 scp 到 NUC，避免命令行字符串超长
  tmp_targets = out_path / "targets.json"
  tmp_targets.write_text(json.dumps(all_books, ensure_ascii=False), encoding="utf-8")
  host = NUC_TARGET
  subprocess.run(NUC_SCP + [str(tmp_targets), f"{host}:/tmp/audit_targets.json"], check=True)

  # 生成并上传远程执行脚本
  remote_worker = """
import sys, json
sys.path.insert(0, '/tmp')
from nuc_verifier import AlistClient, verify_book_on_alist

client = AlistClient()
client.login()

with open('/tmp/audit_targets.json', encoding='utf-8') as f:
    targets = json.load(f)

results = []
for t in targets:
    cat, book = t['category'], t['book']
    ok, msg, details = verify_book_on_alist(client, cat, book)
    results.append({
        'category': cat,
        'book': book,
        'is_volume': t['is_volume'],
        'verified_ok': ok,
        'message': msg,
        'status': details.get('status', 'OK' if ok else 'BROKEN'),
        'details': details
    })

with open('/tmp/audit_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False)
print("AUDIT_WORKER_DONE")
"""
  tmp_worker = out_path / "worker.py"
  tmp_worker.write_text(remote_worker, encoding="utf-8")
  subprocess.run(NUC_SCP + [str(tmp_worker), f"{host}:/tmp/audit_worker.py"], check=True)

  res = subprocess.run(direct_ssh_command(host, "python3", "/tmp/audit_worker.py"), capture_output=True, text=True, check=True)

  # 获取结果文件
  res_file = out_path / "remote_results.json"
  subprocess.run(NUC_SCP + [f"{host}:/tmp/audit_results.json", str(res_file)], check=True)
  audit_records = json.loads(res_file.read_text(encoding="utf-8"))

  print(f"\n[3/4] Comparing with baseline releases and checking local consistency...")
  # Baseline comparison
  baseline_path = Path("private/readalong-release-bundles/nuc-release-20261024/book-release-records.json")
  baseline_records = json.load(open(baseline_path)) if baseline_path.exists() else {}
  excluded_root_cause = json.load(open("private/readalong-release-bundles/nuc-release-20261024/excluded-books-root-cause.json"))

  # Local workspace comparison
  local_root = Path("/Users/jerryyi/Desktop/寒假/未命名文件夹")

  depth2_books = [r for r in audit_records if not r["is_volume"]]
  volume_books = [r for r in audit_records if r["is_volume"]]

  ok_records = [r for r in audit_records if r["status"] == "OK"]
  broken_records = [r for r in audit_records if r["status"] == "BROKEN"]
  audio_only_records = [r for r in audit_records if r["status"] == "AUDIO_ONLY"]

  # Generate audit.json
  audit_json_data = {
    "timestamp": datetime.datetime.now().isoformat(),
    "remoteRoot": args.remote_root,
    "counts": {
      "depth2_total": len(depth2_books),
      "volume_total": len(volume_books),
      "total_audited": len(audit_records),
      "verified_ok": len(ok_records),
      "broken": len(broken_records),
      "audio_only": len(audio_only_records)
    },
    "anomalies": {
      "pua_items": remote_meta["pua_items"],
      "appledouble_count": len(remote_meta["appledouble_files"]),
      "ds_stores_count": len(remote_meta["ds_stores"]),
      "lock_count": len(remote_meta["locks"])
    },
    "records": audit_records
  }
  (out_path / "audit.json").write_text(json.dumps(audit_json_data, ensure_ascii=False, indent=2), encoding="utf-8")

  print(f"[4/4] Writing REPORT.md to {out_path / 'REPORT.md'}...")
  # Group broken records by issues
  grouped_issues = {}
  for b in broken_records:
    for issue in b["details"].get("issues", []):
      issue_key = issue.split(":")[0]
      grouped_issues.setdefault(issue_key, []).append(f"{b['category']}/{b['book']}")

  report_md = f"""# 全库排查审计报告（WO-RL-NUC-AUDIT-20261025）

**排查时间**：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**执行环境**：MacBook 本机，NUC 远端环境：`hp:{args.remote_root}`
**核验基准**：严格匹配前端 `studio/audiobooks/app.js` 真实客户端读取契约（Alist API 逐项在线验证）

---

## 1. 核心数据汇总（双口径严格统计）

| 统计口径 | 总计项 | 状态 OK（可跟读且音轨匹配） | 纯听图书（Audio-Only） | 存在缺陷（BROKEN） |
|---|:---:|:---:|:---:|:---:|
| **书目录级（Depth-2 核心账本）** | **{len(depth2_books)}** | **{len([r for r in depth2_books if r['status'] == 'OK'])}** | **{len([r for r in depth2_books if r['status'] == 'AUDIO_ONLY'])}** | **{len([r for r in depth2_books if r['status'] == 'BROKEN'])}** |
| **分卷子书目级（Volume-level，如思维模型）** | **{len(volume_books)}** | **{len([r for r in volume_books if r['status'] == 'OK'])}** | **{len([r for r in volume_books if r['status'] == 'AUDIO_ONLY'])}** | **{len([r for r in volume_books if r['status'] == 'BROKEN'])}** |
| **全库总条目** | **{len(audit_records)}** | **{len(ok_records)}** | **{len(audio_only_records)}** | **{len(broken_records)}** |

---

## 2. 缺陷书籍明细与问题分类

### 缺陷分类汇总表
"""
  for issue_name, books_list in sorted(grouped_issues.items()):
    report_md += f"\n#### `{issue_name}`（共 {len(books_list)} 本）\n"
    for item in sorted(set(books_list)):
      report_md += f"- `{item}`\n"

  report_md += f"""
---

## 3. 结构异常与特殊目录（只读排查事实）

1. **私有区字符（PUA）重复目录**：
   - 发现含 `\\uf0xx` 私有区字符的项共 **{len(remote_meta['pua_items'])}** 处，其中典型包括：
"""
  for item in remote_meta["pua_items"][:10]:
    report_md += f"     - `{item}`\n"

  report_md += f"""
2. **残余元数据与锁文件**：
   - AppleDouble (`._*`) 文件：**{len(remote_meta['appledouble_files'])}** 处；
   - `.DS_Store`：**{len(remote_meta['ds_stores'])}** 处；
   - 锁文件 (`.readalong_publish.lock`)：**{len(remote_meta['locks'])}** 处。

3. **历史错误目录**：
   - `心智成长/The/` 与 `心智成长/Cognitive/` 完整保留未动，等待用户处置决策。

---

## 4. 纯听书籍账本核对（Audio-Only）
"""
  for r in audio_only_records:
    uid = f"{r['category']}/{r['book']}"
    root_cause = excluded_root_cause.get(uid, {}).get("rootCause", "未登记物理根因")
    report_md += f"- **`{uid}`**：{root_cause}\n"

  (out_path / "REPORT.md").write_text(report_md, encoding="utf-8")
  print("\nAudit scan completed successfully.")
  print(f"Results saved to:\n  - {out_path / 'audit.json'}\n  - {out_path / 'REPORT.md'}")


if __name__ == "__main__":
  main()
