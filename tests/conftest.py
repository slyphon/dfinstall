from pathlib import Path

import pytest


def ignore(*a, **kw):
  pass


def safermtree(p):
  rmtree(p, onerror=ignore)


def copy_fn(src, dst, *a, **kw):
  print(f"cp {src} -> {dst}", file=sys.stderr)
  copy2(src, dst, *a, **kw)


def assert_symlink_same_file(link: Path, target: Path):
  assert link.samefile(target)

