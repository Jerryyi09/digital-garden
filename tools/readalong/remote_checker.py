import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nuc_verifier import AlistClient, verify_book_on_alist

if len(sys.argv) < 3:
  print("Usage: python3 remote_checker.py <category> <book_name>")
  sys.exit(1)

cat, book = sys.argv[1], sys.argv[2]
sample_only = "--sample" in sys.argv[3:]
c = AlistClient()
res = verify_book_on_alist(c, cat, book, sample_only=sample_only)
ok, msg = res[0], res[1]
print(f"VERIFY:{ok}:{msg}")
if not ok:
  sys.exit(1)
