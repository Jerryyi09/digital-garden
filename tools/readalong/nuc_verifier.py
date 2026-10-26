"""NUC Alist verification and library auditing matching studio/audiobooks/app.js client rules."""
import json
from pathlib import Path
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET


class AlistClient:
  def __init__(self, base_url="http://127.0.0.1:5244/alist", username="hp", password="hp", timeout=15):
    self.base_url = base_url.rstrip("/")
    self.username = username
    self.password = password
    self.timeout = timeout
    self.token = None

  def _post(self, path, payload, token=None):
    url = f"{self.base_url}/api/{path.lstrip('/')}"
    headers = {"Content-Type": "application/json"}
    if token:
      headers["Authorization"] = token
    data = json.dumps(payload).encode("utf-8")
    for attempt in range(3):
      try:
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
          return json.loads(resp.read().decode("utf-8"))
      except Exception:
        if attempt == 2:
          raise
        import time
        time.sleep(1)

  def login(self):
    res = self._post("auth/login", {"username": self.username, "password": self.password})
    if res.get("code") == 200 and res.get("data", {}).get("token"):
      self.token = res["data"]["token"]
      return self.token
    raise RuntimeError(f"Alist login failed: {res.get('message')}")

  def ensure_token(self):
    if not self.token:
      self.login()
    return self.token

  def list_dir(self, path, refresh=True):
    self.ensure_token()
    page = 1
    all_content = []
    first_res = None
    while True:
      res = self._post("fs/list", {"path": path, "refresh": bool(refresh and page == 1), "page": page, "per_page": 1000}, self.token)
      if not first_res:
        first_res = res
      if res.get("code") != 200:
        return res
      content = res.get("data", {}).get("content") or []
      all_content.extend(content)
      total = res.get("data", {}).get("total", len(content))
      if len(all_content) >= total or not content:
        break
      page += 1
    if first_res and "data" in first_res and isinstance(first_res["data"], dict):
      first_res["data"]["content"] = all_content
    return first_res

  def get_file_info(self, path):
    self.ensure_token()
    return self._post("fs/get", {"path": path}, self.token)

  def fetch_raw(self, path):
    info = self.get_file_info(path)
    if info.get("code") != 200 or not info.get("data", {}).get("raw_url"):
      return None, info.get("message", "file not found")
    raw_url = info["data"]["raw_url"]
    for attempt in range(3):
      try:
        req = urllib.request.Request(raw_url, headers={"User-Agent": "NucVerifier/1.0"})
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
          return resp.read(), None
      except Exception:
        if attempt == 2:
          raise
        import time
        time.sleep(1)

  def fetch_json(self, path):
    raw, err = self.fetch_raw(path)
    if raw is None:
      return None, err
    try:
      return json.loads(raw.decode("utf-8")), None
    except Exception as e:
      return None, f"JSON parse error: {e}"


def simulate_client_track_matching(manifest: dict, timeline: list, book_path: str, tracks: list[dict]):
  """Strictly simulates client track matching in app.js line 1230."""
  matched_tracks = []
  unmatched_tracks = []
  audio_sources = manifest.get("audioSources") or []

  for t in tracks:
    t_path = t.get("path") or f"{book_path}/{t['name']}"
    t_name = t["name"]
    relative = t_path[len(book_path) + 1:] if t_path.startswith(book_path) else t_name

    source = next((s for s in audio_sources if s.get("id") == relative or s.get("alistPath") == t_path or s.get("id") == t_name or s.get("name") == t_name), None)
    matched = []
    if source:
      sid = source.get("id")
      matched = [s for s in timeline if s.get("audioSourceId") == sid or s.get("audioSourceId") == t_name]
    if not matched:
      matched = [s for s in timeline if s.get("audioSourceId") == t_name or s.get("audioSourceId") == relative]
    if not matched and not any(s.get("audioSourceId") for s in timeline):
      matched = timeline

    if matched:
      matched_tracks.append({"track": t_name, "segments": len(matched)})
    else:
      unmatched_tracks.append(t_name)

  return matched_tracks, unmatched_tracks


def verify_book_on_alist(client: AlistClient, category: str, book_name: str, alist_root: str = "/750HD/有声书"):
  """Comprehensive audit of a book through Alist matching client app.js rules."""
  book_path = f"{alist_root.rstrip('/')}/{category}/{book_name}"
  issues = []
  details = {}

  # 1. 刷新书目录并获取物理文件列表
  try:
    b_list = client.list_dir(book_path, refresh=True)
    if b_list.get("code") != 200:
      return False, f"Failed listing book dir {book_path}: {b_list.get('message')}", {"issues": ["DIR_NOT_FOUND"]}
    client.list_dir(f"{book_path}/readalong", refresh=True)
  except Exception as e:
    return False, f"Network or Alist error for {book_path}: {e}", {"issues": ["NETWORK_ERROR"]}

  content_files = b_list.get("data", {}).get("content", [])
  physical_audios = [f for f in content_files if not f.get("is_dir") and f.get("name", "").lower().endswith((".mp3", ".m4b", ".m4a", ".aac"))]
  physical_epubs = [f for f in content_files if not f.get("is_dir") and f.get("name", "").lower().endswith(".epub")]
  has_cover = any(f.get("name", "").lower() in ("cover.jpg", "cover.jpeg", "folder.jpg") for f in content_files)
  has_summary = any(f.get("name", "") == "summary.txt" for f in content_files)

  details["audio_count"] = len(physical_audios)
  details["epub_count"] = len(physical_epubs)
  details["has_cover"] = has_cover
  details["has_summary"] = has_summary

  # 2. 读取 manifest
  manifest_path = f"{book_path}/readalong/readalong.manifest.json"
  manifest, err = client.fetch_json(manifest_path)
  if not manifest:
    if len(physical_audios) > 0 and len(physical_epubs) > 0:
      issues.append("MANIFEST_MISSING_FOR_AUDIO_AND_EPUB")
    return False, f"Manifest missing or unreadable: {manifest_path} ({err})", {"issues": issues, "details": details}

  if manifest.get("schemaVersion") != 1:
    issues.append("SCHEMA_VERSION_INVALID")

  readalong_enabled = manifest.get("readalongEnabled") is True
  details["readalongEnabled"] = readalong_enabled
  if not readalong_enabled:
    # 纯音频或排除图书
    return True, "AUDIO_ONLY", {"status": "AUDIO_ONLY", "manifest": manifest, "details": details}

  # 3. 解析 assetBase 与 timeline 路径
  asset_rev = manifest.get("assetRevision") or ""
  details["assetRevision"] = asset_rev or None
  if re.fullmatch(r"[a-f0-9]{32}", asset_rev):
    asset_base = f"{book_path}/.readalong_revisions/{asset_rev}"
    try:
      client.list_dir(asset_base, refresh=True)
    except Exception:
      pass
  else:
    asset_base = f"{book_path}/readalong"

  timeline_name = manifest.get("timeline") or "timeline.json"
  timeline_path = f"{asset_base}/{timeline_name}"

  # 4. 获取 timeline 并检查非空数组
  timeline, err = client.fetch_json(timeline_path)
  if not isinstance(timeline, list) or len(timeline) == 0:
    issues.append(f"TIMELINE_UNREADABLE: {timeline_path} ({err})")
    timeline = []
  details["timeline_segments"] = len(timeline)

  # 5. 校验 URL 编码 (%20 等)
  url_encoded_docs = [s.get("document") for s in timeline if s.get("document") and "%" in s.get("document")]
  if url_encoded_docs:
    issues.append(f"TIMELINE_DOCUMENT_URL_ENCODED: {len(url_encoded_docs)} segments have '%' in document path (sample: {url_encoded_docs[0]})")

  # 6. 校验 audioSources 列表中每个 alistPath
  audio_sources = manifest.get("audioSources") or []
  if not audio_sources:
    issues.append("AUDIO_SOURCES_EMPTY")

  known_source_ids = set()
  for s in audio_sources:
    sid = s.get("id") or s.get("name")
    if sid:
      known_source_ids.add(sid)
    alist_path = s.get("alistPath")
    if not alist_path:
      issues.append(f"AUDIO_SOURCE_MISSING_ALIST_PATH: {s}")
    else:
      info = client.get_file_info(alist_path)
      if info.get("code") != 200:
        issues.append(f"AUDIO_SOURCE_ALIST_PATH_NOT_FOUND: {alist_path}")

  # 7. timeline segment audioSourceId 校验
  unmatched_seg_sources = set()
  for seg in timeline:
    as_id = seg.get("audioSourceId")
    if as_id and as_id not in known_source_ids:
      unmatched_seg_sources.add(as_id)
  if unmatched_seg_sources:
    issues.append(f"TIMELINE_SEGMENT_AUDIO_UNREGISTERED: {sorted(unmatched_seg_sources)}")

  # 8. 逐条模拟前端的音轨匹配
  matched_tracks, unmatched_tracks = simulate_client_track_matching(manifest, timeline, book_path, physical_audios)
  details["matched_tracks"] = matched_tracks
  details["unmatched_tracks"] = unmatched_tracks
  if len(physical_audios) > 0 and len(matched_tracks) == 0:
    issues.append("NO_AUDIO_TRACKS_MATCHED_CLIENT_RULES")

  # 9. textRoot 与 OPF / spine 检查
  text_root = manifest.get("textRoot") or "text/"
  text_base = f"{asset_base}/{text_root.rstrip('/')}"
  try:
    t_list = client.list_dir(text_base, refresh=True)
    if t_list.get("code") != 200:
      issues.append(f"TEXT_ROOT_UNREADABLE: {text_base}")
    else:
      # 寻找 OPF
      opf_raw, _ = client.fetch_raw(f"{text_base}/content.opf")
      if not opf_raw:
        opf_raw, _ = client.fetch_raw(f"{text_base}/OEBPS/content.opf")
      if not opf_raw:
        # 递归寻找 .opf
        c_files = t_list.get("data", {}).get("content", [])
        opf_f = next((f["name"] for f in c_files if f.get("name", "").endswith(".opf")), None)
        if opf_f:
          opf_raw, _ = client.fetch_raw(f"{text_base}/{opf_f}")
      if not opf_raw:
        # 兼容性检查：若有 container.xml 则解析其 rootfile
        c_xml, _ = client.fetch_raw(f"{text_base}/META-INF/container.xml")
        if c_xml:
          try:
            c_tree = ET.fromstring(c_xml)
            rf = c_tree.find(".//{*}rootfile")
            if rf is not None and rf.attrib.get("full-path"):
              opf_raw, _ = client.fetch_raw(f"{text_base}/{rf.attrib['full-path']}")
          except Exception:
            pass
      if not opf_raw:
        issues.append(f"OPF_MISSING_IN_TEXT_ROOT: {text_base}")
  except Exception as e:
    issues.append(f"TEXT_ROOT_CHECK_EXCEPTION: {e}")

  # 10. 检查封面和简介（匹配前端逐级向上支持：若分卷无，向上查找父目录封面与简介）
  if not has_cover and "/" in book_name:
    parent_book_name = book_name.rsplit("/", 1)[0]
    p_info = client.list_dir(f"{alist_root.rstrip('/')}/{category}/{parent_book_name}", refresh=False)
    p_files = p_info.get("data", {}).get("content", [])
    has_cover = any(f.get("name", "").lower() in ("cover.jpg", "cover.jpeg", "folder.jpg") for f in p_files)

  if not has_summary and "/" in book_name:
    parent_book_name = book_name.rsplit("/", 1)[0]
    p_info = client.list_dir(f"{alist_root.rstrip('/')}/{category}/{parent_book_name}", refresh=False)
    p_files = p_info.get("data", {}).get("content", [])
    has_summary = any(f.get("name", "") == "summary.txt" for f in p_files)

  if not has_cover:
    issues.append("COVER_MISSING")
  if not has_summary:
    issues.append("SUMMARY_MISSING")

  ok = len(issues) == 0
  status = "OK" if ok else "BROKEN"
  details["issues"] = issues
  details["status"] = status
  msg = "OK" if ok else "; ".join(issues)
  return ok, msg, details


def verify_book_via_ssh(remote_host: str, category: str, book_name: str, alist_root: str = "/750HD/有声书"):
  """Run verification remotely via direct SSH using /tmp/remote_checker.py."""
  import subprocess
  from tools.readalong.nuc_target import direct_ssh_command
  cmd = direct_ssh_command(remote_host, f'python3 /tmp/remote_checker.py "{category}" "{book_name}"')
  res = subprocess.run(cmd, capture_output=True, text=True)
  out = res.stdout.strip()
  if res.returncode == 0 and "VERIFY:True" in out:
    return True, "OK"
  return False, res.stderr.strip() or out
