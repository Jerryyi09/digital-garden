"""Run on the NUC to deploy the audiobook search service from a staged directory."""
import datetime
import shutil
import subprocess
import sys
from pathlib import Path

SERVICE_DIR = Path('/home/hp/.local/lib/garden-sync')
DATA_DIR = Path('/home/hp/.local/share/garden-sync')
NGINX_CONF = Path('/home/hp/docker-compose/nginx/conf.d/melyi.uk.conf')
BACKUP_ROOT = Path('/home/hp/docker-compose/nginx/backups')
LIBRARY_ROOT = Path('/mnt/750/Music/有声书')
ALIST_ROOT = '/多媒体/750HD/有声书'
SEARCH_LOCATION = '''\n    location = /sync/v1/search {
        proxy_pass http://garden-audiobook-sync:8791;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_connect_timeout 5s;
        proxy_read_timeout 15s;
    }\n'''


def run(*command):
  subprocess.run(command, check=True)


def block_end(text, start):
  depth = 0
  for index in range(start, len(text)):
    if text[index] == '{':
      depth += 1
    elif text[index] == '}':
      depth -= 1
      if depth == 0:
        return index + 1
  raise ValueError('unterminated Nginx location block')


def updated_nginx_config(text):
  if 'location = /sync/v1/search' in text:
    return text
  start = text.find('location = /sync/v1/items')
  if start < 0:
    raise ValueError('existing /sync/v1/items location is missing')
  end = block_end(text, start)
  return text[:end] + SEARCH_LOCATION + text[end:]


def main(stage):
  stage = Path(stage).resolve()
  required = ('server.py', 'library_index.py', 'backup.py')
  if not stage.is_dir() or any(not (stage / name).is_file() for name in required):
    raise ValueError('staged service files are incomplete')
  run('python3', '-m', 'py_compile', *(str(stage / name) for name in required))
  timestamp = datetime.datetime.now(datetime.UTC).strftime('%Y%m%dT%H%M%SZ')
  backup = BACKUP_ROOT / f'garden-sync-search-{timestamp}'
  backup.mkdir(mode=0o700, parents=True)
  for name in ('server.py', 'backup.py'):
    shutil.copy2(SERVICE_DIR / name, backup / name)
  if (SERVICE_DIR / 'library_index.py').exists():
    shutil.copy2(SERVICE_DIR / 'library_index.py', backup / 'library_index.py')
  shutil.copy2(NGINX_CONF, backup / 'melyi.uk.conf')
  run('python3', str(SERVICE_DIR / 'backup.py'), str(DATA_DIR / 'sync.sqlite3'), str(backup / 'sync.sqlite3'))
  try:
    for name in required:
      shutil.copy2(stage / name, SERVICE_DIR / name)
    NGINX_CONF.write_text(updated_nginx_config(NGINX_CONF.read_text()), encoding='utf-8')
    run('docker', 'exec', 'nginx', 'nginx', '-t')
    run('docker', 'restart', 'garden-audiobook-sync')
    run('docker', 'exec', 'nginx', 'nginx', '-s', 'reload')
    run('python3', str(SERVICE_DIR / 'library_index.py'), str(DATA_DIR / 'sync.sqlite3'), str(LIBRARY_ROOT), ALIST_ROOT)
  except BaseException:
    for name in ('server.py', 'backup.py', 'library_index.py'):
      source = backup / name
      if source.exists():
        shutil.copy2(source, SERVICE_DIR / name)
    shutil.copy2(backup / 'melyi.uk.conf', NGINX_CONF)
    run('docker', 'restart', 'garden-audiobook-sync')
    run('docker', 'exec', 'nginx', 'nginx', '-s', 'reload')
    raise
  print(f'Deployed global search. Backup: {backup}')


if __name__ == '__main__':
  if len(sys.argv) != 2:
    raise SystemExit('usage: deploy-nuc.py STAGED_DIRECTORY')
  main(sys.argv[1])
