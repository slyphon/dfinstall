import os
import sys
from pathlib import Path
from os.path import abspath, join, dirname
from shutil import copytree, ignore_patterns, rmtree, copy2
from tempfile import TemporaryDirectory

from . import do_the_symlinking

import pytest

THIS_DIR = Path(dirname(abspath(__file__)))


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


FILE_NAMES = ['bashrc', 'gitconfig', 'gitignores', 'profile']


def runit(dir: Path):
  """captures the staged path so that we don't call do_the_symlinking with some dumb dir by accident"""
  def wrapped():
    do_the_symlinking(dir)

  return wrapped


def test_behavior(staged: Path):
  run = runit(staged)
  assert (staged / 'bashrc').exists()
  base = staged.parent
  run()
  for name in FILE_NAMES:
    assert_symlink_same_file(base / f'.{name}', staged / name)

  do_the_symlinking(staged)
  for name in FILE_NAMES:
    assert_symlink_same_file(base / f'.{name}', staged / name)

  for name in FILE_NAMES:
    dotf = base / f'.{name}.000'  # assert we didn't back up the symlinks
    assert not dotf.exists()

  # test a symlink that points somewhere goofy
  dot_bashrc: Path = base / '.bashrc'
  dot_bashrc.unlink()
  dot_bashrc.symlink_to("/this/doesnt/exist")
  run()

  dot_bashrc.unlink()
  os.mkfifo(dot_bashrc)
  with pytest.raises(RuntimeError):
    run()
