from pathlib import Path

import pytest


def ignore(*a, **kw):
  pass


def safermtree(p):
  rmtree(p, onerror=ignore)


def copy_fn(src, dst, *a, **kw):
  print(f"cp {src} -> {dst}", file=sys.stderr)
  copy2(src, dst, *a, **kw)


@pytest.fixture()
def staged(tmpdir):
  tempdir = Path(tmpdir)
  base_dir = tempdir / 'base'
  safermtree(base_dir)
  settings_dir = base_dir / 'settings'

  copytree(
    THIS_DIR.parent, settings_dir, copy_function=copy_fn, ignore=ignore_patterns('.*', '__*__')
  )
  yield settings_dir
  safermtree(base_dir)


def assert_symlink_same_file(link: Path, target: Path):
  assert link.samefile(target)

