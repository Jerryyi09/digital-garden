"""Shared direct-LAN NUC connection and publication lock configuration."""
from contextlib import contextmanager
import fcntl
from pathlib import Path
import subprocess
import time

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


# ssh exits 255 on connection-level failure; rsync uses 12/30/35/255 for transport failures.
# A Wi-Fi blip mid-batch used to abort the whole category (10-26 文学理论) with the reason swallowed.
RETRYABLE_EXIT_CODES = {255, 12, 30, 35}
RETRY_DELAYS_SECONDS = (3, 10)


class NucCommandError(subprocess.CalledProcessError):
  def __str__(self):
    base = f"NUC command exited {self.returncode}: {self.cmd!r}"
    tail = self.stderr
    if isinstance(tail, bytes):
      tail = tail.decode("utf-8", "replace")
    tail = tail.strip()[-800:] if isinstance(tail, str) else ""
    return base + (f"\nremote stderr: {tail}" if tail else "")


def run_nuc(cmd, *, check=True, retries=len(RETRY_DELAYS_SECONDS) + 1, sleep=time.sleep, runner=None, **kwargs):
  """Run an ssh/rsync command against the NUC, retrying transport failures and surfacing stderr.

  Callers pass their own module's ``subprocess.run`` as ``runner`` so tests that patch it still apply.
  """
  runner = runner or subprocess.run
  for attempt in range(1, retries + 1):
    result = runner(cmd, **kwargs)
    code = result.returncode if isinstance(result.returncode, int) else 0
    if code == 0 or code not in RETRYABLE_EXIT_CODES or attempt == retries:
      break
    sleep(RETRY_DELAYS_SECONDS[min(attempt - 1, len(RETRY_DELAYS_SECONDS) - 1)])
  if check and isinstance(result.returncode, int) and result.returncode != 0:
    raise NucCommandError(result.returncode, cmd, output=result.stdout, stderr=result.stderr)
  return result
