import sys

if sys.version_info[0:2] < (3, 6):
  print("This script requires python >= 3.6", file=sys.stderr)
  sys.exit(44)

