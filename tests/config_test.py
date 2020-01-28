import json
from pathlib import Path
from pprint import pprint
from typing import Any, Type, TypeVar

import cattr

from dfi.config import FileGroup, Settings, LinkData

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
    )
    for b in bins
  ]

  dotfiles = ['bash_profile', 'bashrc', 'inputrc', 'vimrc']
  ld_df = [
    LinkData(
      vpath=df_paths.dotfiles_dir.joinpath(df),
      link_path=df_paths.home_dir / f".{df}",
      link_data=Path(df_paths.base_dir.name) / 'dotfiles' / df,
    )
    for df in dotfiles
  ]

  assert s.link_data == [*ld_bins, *ld_df]

  pprint(cattr.unstructure(s.link_data))


def test_Settings_with_globs(df_paths: FixturePaths):
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

  s.link_data
  1 / 0
