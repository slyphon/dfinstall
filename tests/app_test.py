import json
import os
from contextlib import contextmanager
from functools import wraps
from itertools import chain
from pathlib import Path
from pprint import pprint
from typing import ContextManager, Iterator, List, TypeVar, Union

import attr
import cattr
import pytest
from click.testing import CliRunner, Result

from dfinstall import app
from dfinstall.config import Settings, FileGroup

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

  dotfile_extras = [dotfile_extras_dir.joinpath(df) for df in ['tux', 'gnome', '.dfe_ignore']]

  bins = [bin_dir.joinpath(bin) for bin in ['ctags', 'pants', 'pip', '.b_ignore']]

  bin_extras = [binfile_extras_dir.joinpath(b) for b in ['launched', 'pbcopy', '.be_ignore']]

  for f in chain(dotfiles, dotfile_extras, bins, bin_extras):
    f.touch()

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


def test_app_flag_parsing_dotfiles(df_paths, cli_runner):
  dotfiles_arg = ':'.join(
    [str(df.relative_to(df_paths.base_dir)) for df in df_paths.dotfile_extras]
  )

  with chdir(df_paths.base_dir):
    result: Result = cli_runner.invoke(
      app.main,
      # yapf: disable
      args=[
        '--file-conflict-strategy=delete',
        '--symlink-conflict-strategy=fail',
        f'--dotfile-dir={df_paths.dotfiles_dir}',
        f'--dotfiles={dotfiles_arg}',
        '--dotfile-excludes', '.*:tux',
        '--output-flag-settings', '-',
      ]
      # yapf: enable
    )

    assert result.exit_code == 0
    assert len(result.output) > 0

    ser_set = json.loads(result.output)

    settings: Settings = cattr.structure(ser_set, Settings)

    assert settings.base_dir == df_paths.base_dir
    assert settings.conflicting_file_strategy == 'delete'
    assert settings.conflicting_symlink_strategy == 'fail'

    assert settings.dotfiles_file_group == FileGroup(
      dirs=[df_paths.dotfiles_dir],
      globs=dotfiles_arg.split(":"),
      excludes=['.*', 'tux'],
      target_dir=df_paths.home_dir
    )

    assert settings.binfiles_file_group == FileGroup(
      dirs=[],
      globs=None,
      excludes=None,
      target_dir=df_paths.home_dir / '.local' / 'bin'
    )
