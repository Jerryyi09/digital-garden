"""Deploy the audiobook Studio app on the documented NUC, with recoverable backups."""

import datetime
import pathlib
import re
import shutil
import subprocess
import sys


def patch_nginx(source):
  first_end = source.find("\nserver {", source.find("server {") + 1)
  if first_end < 0:
    raise ValueError("Expected separate HTTP and HTTPS server blocks")
  http, rest = source[:first_end], source[first_end:]
  if "listen 80;" not in http or "proxy_pass http://alist:5244;" not in rest:
    raise ValueError("Nginx configuration differs from the documented NUC")
  # The existing default.conf is a separate HTTP vhost; match the LAN IP explicitly.
  name = re.search(r"server_name\s+([^;]+);", http)
  if not name:
    raise ValueError("Cannot identify the HTTP virtual host")
  if "10.0.0.85" not in name.group(1).split():
    http = http[:name.end(1)] + " 10.0.0.85" + http[name.end(1):]
  if "location /alist" not in http:
    marker = "    location /.well-known/acme-challenge/ {"
    if marker not in http:
      raise ValueError("Cannot find safe insertion point for LAN proxy")
    block = """    # LAN audiobook API and signed media streams.
    location /alist {
        proxy_pass http://alist:5244;
        proxy_set_header Host $http_host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header Range $http_range;
        proxy_set_header If-Range $http_if_range;
        proxy_buffering off;
        proxy_redirect / /alist/;
        proxy_redirect /alist:5244/ /alist/;
    }

"""
    http = http.replace(marker, block + marker, 1)

  def disable_buffering(match):
    block = match.group(0)
    if "proxy_buffering" not in block:
      return block[:-1] + "    proxy_buffering off;\n    }"
    return block

  return re.sub(r"location /alist\s*\{[^{}]*\}", disable_buffering, http + rest)


def main():
  stage = pathlib.Path(sys.argv[1]).resolve()
  if not re.fullmatch(r"/tmp/garden-audiobooks\.[a-zA-Z0-9]+", str(stage)):
    raise ValueError("Unexpected staging directory")
  root = pathlib.Path("/home/hp/docker-compose/nginx")
  config = root / "conf.d/melyi.uk.conf"
  studio = root / "html/studio"
  original = config.read_text()
  proposed = patch_nginx(original)
  if not (stage / "audiobooks/app.js").is_file() or not (stage / "index.html").is_file():
    raise ValueError("Incomplete build")
  backup = root / "backups" / ("audiobooks-" + datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
  backup.mkdir(parents=True, exist_ok=False)
  shutil.copy2(config, backup / "melyi.uk.conf")
  shutil.copytree(studio, backup / "studio")
  try:
    config.write_text(proposed)
    subprocess.run(["docker", "exec", "nginx", "nginx", "-t"], check=True)
    shutil.copytree(stage / "audiobooks", studio / "audiobooks", dirs_exist_ok=True)
    shutil.copy2(stage / "index.html", studio / "index.html")
    subprocess.run(["docker", "exec", "nginx", "nginx", "-s", "reload"], check=True)
  except Exception:
    shutil.copy2(backup / "melyi.uk.conf", config)
    # Preserve failed assets for inspection instead of deleting any directory.
    failed = backup / "failed-studio"
    studio.rename(failed)
    shutil.copytree(backup / "studio", studio)
    subprocess.run(["docker", "exec", "nginx", "nginx", "-t"], check=False)
    subprocess.run(["docker", "exec", "nginx", "nginx", "-s", "reload"], check=False)
    raise
  print(f"Deployed audiobook Studio. Backup: {backup}")


if __name__ == "__main__":
  main()
