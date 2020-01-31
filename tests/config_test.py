import os
import json
from pathlib import Path
from pprint import pprint
from typing import Any, List, Type, TypeVar, Tuple, Sequence

# mypy: ignore-missing-imports
from dfi.exceptions import FatalConflict # type: ignore

import attr
import cattr
import pytest

# mypy: ignore-missing-imports
from dfi.config import FileGroup, Settings  # type: ignore # noqa
from dfi.dotfile import LinkData  # type: ignore # noqa
from dfi.fs import apply_settings  # type: ignore

from .conftest import FixturePaths

BASE_DIR = Path("/home/foo/settings")

FG = FileGroup(
  base_dir=BASE_DIR,
  dirs=[Path("/home/foo/settings"), Path("/home/bar/settings")],
  globs=["xyz", "abc"],
  excludes=["*bad", ".ignore*"],
  target_dir=Path("/home/foo")
)

SETTINGS = Settings(
  conflicting_file_strategy='backup',
  conflicting_symlink_strategy='replace',
  base_dir=BASE_DIR,
  dotfiles_file_group=FG,
  binfiles_file_group=FG,
)

T = TypeVar('T')

def do_roundtrip(obj: T, cls: Type[T]):
  return cattr.structure(json.loads(json.dumps(cattr.unstructure(obj))), cls)

def test_FileGroup_json_round_trip():
  assert FG == do_roundtrip(FG, FileGroup)


def test_Settings_round_trip():
  assert SETTINGS == do_roundtrip(SETTINGS, Settings)


def test_Settings_vpaths(df_paths: FixturePaths):
  s = Settings.mk_default(df_paths.base_dir)
  pprint(s.vpaths)
  bins = ['ctags', 'pants', 'pip']
  dotfiles = ['bash_profile', 'bashrc', 'inputrc', 'vimrc']
  vpaths = [
    *[df_paths.bin_dir.joinpath(b) for b in bins],
    *[df_paths.dotfiles_dir.joinpath(d) for d in dotfiles]
  ]
  assert s.vpaths == vpaths


def test_Settings_link_data(df_paths: FixturePaths):
  s = Settings.mk_default(df_paths.base_dir)

  bins = ['ctags', 'pants', 'pip']
  ld_bins = [
    LinkData(
      vpath=df_paths.bin_dir.joinpath(b),
      link_path=df_paths.home_dir / '.local/bin' / b,
      link_data=Path("../..", df_paths.base_dir.name) / 'bin' / b,
    ) for b in bins
  ]

  dotfiles = ['bash_profile', 'bashrc', 'inputrc', 'vimrc']
  ld_df = [
    LinkData(
      vpath=df_paths.dotfiles_dir.joinpath(df),
      link_path=df_paths.home_dir / f".{df}",
      link_data=Path(df_paths.base_dir.name) / 'dotfiles' / df,
    ) for df in dotfiles
  ]

  assert s.link_data == [*ld_bins, *ld_df]

  pprint(cattr.unstructure(s.link_data))



def test_Settings_with_globs_has_correct_precedence(df_paths: FixturePaths):
  s = Settings(
    base_dir=df_paths.base_dir,
    dotfiles_file_group=FileGroup(
      base_dir=df_paths.base_dir,
      target_dir=df_paths.home_dir,
      dirs=[df_paths.dotfiles_dir],
      globs=[str(g.relative_to(df_paths.base_dir)) for g in df_paths.dotfile_extras],
      excludes=['.*', 'gnome'],
      link_prefix='.',
    ),
    binfiles_file_group=FileGroup(
      base_dir=df_paths.base_dir,
      target_dir=df_paths.home_dir.joinpath('.local', 'bin'),
      dirs=[],
      globs=None,
      excludes=None,
    ),
  )
  vpaths: List[Path] = []
  link_paths: List[Path] = []
  link_datas: List[Path] = []

  for ld in s.link_data:
    v, lp, d = ld.vpath, ld.link_path, ld.link_data
    vpaths.append(v.relative_to(df_paths.home_dir))
    link_paths.append(lp.relative_to(df_paths.home_dir))
    link_datas.append(d)

  expect_vpaths = [
    'settings/dotfile_linux/bash_profile',
    'settings/dotfiles/bashrc',
    'settings/dotfiles/inputrc',
    'settings/dotfile_linux/tux',
    'settings/dotfiles/vimrc'
  ]

  assert expect_vpaths == [str(v) for v in vpaths]

  assert ['.bash_profile', '.bashrc', '.inputrc', '.tux', '.vimrc'] == [str(v) for v in link_paths]

  assert expect_vpaths == [str(v) for v in link_datas]

@pytest.fixture()
def settings(df_paths: FixturePaths):
  return Settings(
    base_dir=df_paths.base_dir,
    dotfiles_file_group=FileGroup(
      base_dir=df_paths.base_dir,
      target_dir=df_paths.home_dir,
      dirs=[df_paths.dotfiles_dir],
      globs=[str(g.relative_to(df_paths.base_dir)) for g in df_paths.dotfile_extras],
      excludes=['.*', 'gnome'],
      link_prefix='.',
    ),
    binfiles_file_group=FileGroup(
      base_dir=df_paths.base_dir,
      target_dir=df_paths.home_dir.joinpath('.local', 'bin'),
      dirs=[Path('bin')],
      globs=None,
      excludes=['.*'],
    ),
  )


def test_Settings_install(df_paths: FixturePaths, settings: Settings):
  s = settings
  apply_settings(s)
  print(df_paths.home_dir)

  print(df_paths.home_dir.glob("*"))

  for df in ['.bash_profile', '.bashrc', '.inputrc', '.tux', '.vimrc']:
    link_location = df_paths.home_dir.joinpath(df)
    assert link_location.exists()
    assert link_location.is_symlink()

  for bin in ['ctags', 'pants', 'pip']:
    link_location = df_paths.home_dir.joinpath('.local', 'bin', bin)
    assert link_location.exists()
    assert link_location.is_symlink()



def test_file_conflict_backup(df_paths: FixturePaths, settings: Settings):
  s = settings
  bashrcpath = df_paths.home_dir.joinpath('.bashrc')
  contents = 'export YOUR_MOM=1'
  bashrcpath.write_text(contents, encoding='utf8')
  apply_settings(s)

  backup: List[Path] = list(df_paths.home_dir.glob('.bashrc.dfi_*'))
  assert len(backup) > 0

  assert backup[0].read_text() == contents

def test_file_conflict_delete(df_paths: FixturePaths, settings: Settings):
  s = attr.evolve(settings, conflicting_file_strategy='delete')
  bashrcpath = df_paths.home_dir.joinpath('.bashrc')
  contents = 'export THIS_IS_ONE=1'
  bashrcpath.write_text(contents, encoding='utf8')
  apply_settings(s)

  backup: List[Path] = list(df_paths.home_dir.glob('.bashrc.dfi_*'))
  assert len(backup) == 0
  assert bashrcpath.read_text() == "file: bashrc"


def test_file_conflict_warn(df_paths: FixturePaths, settings: Settings, caplog: Any):
  s = attr.evolve(settings, conflicting_file_strategy='warn')
  bashrcpath = df_paths.home_dir.joinpath('.bashrc')
  contents = 'export THIS_IS_ONE=1'
  bashrcpath.write_text(contents, encoding='utf8')
  apply_settings(s)

  rtup: Sequence[Tuple[str, int, str]] = caplog.record_tuples
  assert len(rtup) >= 1
  file, line, msg = next((t for t in rtup if t[0] == "dfi.fs"))
  assert file == "dfi.fs"
  assert msg.startswith("File location")
  assert msg.endswith("'warn' strategy selected, continuing.")
  assert bashrcpath.read_text(encoding='utf8') == contents

def test_file_conflict_fail(df_paths: FixturePaths, settings: Settings):
  s = attr.evolve(settings, conflicting_file_strategy='fail')
  bashrcpath = df_paths.home_dir.joinpath('.bashrc')
  contents = 'export THIS_IS_ONE=1'
  bashrcpath.write_text(contents, encoding='utf8')

  with pytest.raises(FatalConflict):
    apply_settings(s)

  assert bashrcpath.read_text(encoding='utf8') == contents
