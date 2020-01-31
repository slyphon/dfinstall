import os
from contextlib import contextmanager
from itertools import chain
from pathlib import Path
from pprint import pprint
from typing import ContextManager, Iterator, List, TypeVar, Union, cast

import attr
import cattr
import pytest
from click.testing import CliRunner, Result


def ignore(*a, **kw):
  pass


def safermtree(p):
  rmtree(p, onerror=ignore)


def copy_fn(src, dst, *a, **kw):
  print(f"cp {src} -> {dst}", file=sys.stderr)
  copy2(src, dst, *a, **kw)


def assert_symlink_same_file(link: Path, target: Path):
  assert link.samefile(target)

T = TypeVar('T')


@contextmanager
def chdir(path: Union[str, Path]):
  cwd = os.getcwd()
  try:
    os.chdir(path)
    f = yield
    return f
  finally:
    os.chdir(cwd)


@attr.s(slots=True, frozen=True, auto_attribs=True)
class FixturePaths:
  tmp: Path
  home_dir: Path
  base_dir: Path
  dotfiles_dir: Path
  dotfile_extras_dir: Path
  bin_dir: Path
  binfile_extras_dir: Path
  dotfiles: List[Path]
  dotfile_extras: List[Path]
  bins: List[Path]
  bin_extras: List[Path]


@pytest.fixture()
def cli_runner():
  runner = CliRunner()
  with runner.isolated_filesystem():
    yield runner


@pytest.fixture()
def df_paths(cli_runner):
  tmp = Path(os.getcwd()).resolve()
  home_dir: Path = tmp / "home"
  base_dir: Path = home_dir / "settings"
  dotfiles_dir: Path = base_dir / "dotfiles"
  dotfile_extras_dir: Path = base_dir / "dotfile_linux"
  bin_dir: Path = base_dir / "bin"
  binfile_extras_dir: Path = base_dir / "bin_darwin"

  for d in [home_dir, base_dir, dotfiles_dir, bin_dir, dotfile_extras_dir, binfile_extras_dir]:
    d.mkdir(mode=0o755, parents=True, exist_ok=True)

  dotfiles = [
    dotfiles_dir.joinpath(df)
    for df in ['bashrc', 'vimrc', 'inputrc', 'bash_profile', '.df_ignore']
  ]

  dotfile_extras = [dotfile_extras_dir.joinpath(df) for df in ['tux', 'gnome', '.dfe_ignore', 'bash_profile']]

  bins = [bin_dir.joinpath(bin) for bin in ['ctags', 'pants', 'pip', '.b_ignore']]

  bin_extras = [binfile_extras_dir.joinpath(b) for b in ['launched', 'pbcopy', '.be_ignore']]

  for f in chain(dotfiles, dotfile_extras, bins, bin_extras):
    cast(Path, f).write_text(f"file: {f.name!s}", encoding='utf8')

  yield FixturePaths(
    tmp=tmp,
    home_dir=home_dir,
    base_dir=base_dir,
    dotfiles_dir=dotfiles_dir,
    dotfile_extras_dir=dotfile_extras_dir,
    bin_dir=bin_dir,
    dotfiles=dotfiles,
    bins=bins,
    dotfile_extras=dotfile_extras,
    bin_extras=bin_extras,
    binfile_extras_dir=binfile_extras_dir,
  )
