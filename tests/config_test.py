import cattr
from pathlib import Path
from typing import Type, Any, TypeVar
from dfinstall.config import FileGroup, Settings
import json


FG = FileGroup(
  dirs=[Path("/home/foo/settings"), Path("/home/bar/settings")],
  globs=["xyz", "abc"],
  excludes=["*bad", ".ignore*"],
  target_dir=Path("/home/foo")
)

BASE_DIR = Path("/home/foo/settings")

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
