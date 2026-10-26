"""Read-only NUC backup sizes and modification times; never removes files."""
import json
import shlex
import subprocess

from tools.readalong.nuc_target import NUC_TARGET, direct_ssh_command


REMOTE_REPORT = '''
import datetime, json, os
from pathlib import Path
roots = [Path('/home/hp/readalong-sync-backup'), Path('/home/hp/readalong-manifest-backup-20261025')]
def summarize(path):
  size = allocated = count = 0
  newest = path.stat().st_mtime
  for directory, dirs, files in os.walk(path, followlinks=False):
    for name in files:
      item = Path(directory) / name
      stat = item.lstat()
      size += stat.st_size
      allocated += stat.st_blocks * 512
      count += 1
      newest = max(newest, stat.st_mtime)
  return {'path': str(path), 'files': count, 'bytes': size, 'allocatedBytes': allocated,
          'latestModifiedUTC': datetime.datetime.fromtimestamp(newest, datetime.timezone.utc).isoformat()}
report = []
for root in roots:
  if not root.is_dir():
    report.append({'path': str(root), 'exists': False})
    continue
  row = summarize(root)
  row['children'] = [summarize(p) for p in sorted(root.iterdir()) if p.is_dir() and not p.is_symlink()]
  report.append(row)
print(json.dumps(report, ensure_ascii=False, indent=2))
'''


def backup_report_command():
  return direct_ssh_command(NUC_TARGET, "python3 -c " + shlex.quote(REMOTE_REPORT))


def main():
  result = subprocess.run(backup_report_command(), check=True, capture_output=True, text=True)
  print(json.dumps(json.loads(result.stdout), ensure_ascii=False, indent=2))


if __name__ == "__main__":
  main()
