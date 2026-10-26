"""Shared direct-LAN NUC connection and publication lock configuration."""
from contextlib import contextmanager
import fcntl
from pathlib import Path

NUC_TARGET = "hp@10.0.0.85"
NUC_PORT = "2222"
NUC_KEY = Path.home() / ".ssh" / "id_rsa"
NUC_SSH = ["ssh", "-F", "/dev/null", "-p", NUC_PORT, "-i", str(NUC_KEY),
           "-o", "BatchMode=yes", NUC_TARGET]
NUC_RSYNC_E = f"ssh -F /dev/null -p {NUC_PORT} -i {NUC_KEY} -o BatchMode=yes"
NUC_SCP = ["scp", "-F", "/dev/null", "-P", NUC_PORT, "-i", str(NUC_KEY), "-o", "BatchMode=yes"]
NUC_REMOTE_BASE = "/mnt/750/Music/有声书"
NUC_LOCK_PATH = Path("/tmp/readalong-publish-nuc.lock")


@contextmanager
def nuc_publication_lock():
  """Hold the cross-process NUC publication lock for the whole operation."""
  with NUC_LOCK_PATH.open("a+") as lock_file:
    try:
      fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as exc:
      raise RuntimeError(f"Another NUC publication process is running ({NUC_LOCK_PATH})") from exc
    try:
      yield
    finally:
      fcntl.flock(lock_file, fcntl.LOCK_UN)


def canonical_nuc_target(host):
  if host in ("hp", "10.0.0.85", NUC_TARGET):
    return NUC_TARGET
  raise ValueError(f"NUC connections must use the configured direct LAN target {NUC_TARGET}; got {host!r}")


def direct_ssh_command(host, *remote_args):
  """Build a host-config-independent direct SSH command."""
  return NUC_SSH[:-1] + [canonical_nuc_target(host), *remote_args]
