from pathlib import Path
from functools import partial
from typing import Callable, Iterable, List, Optional, Type, cast, TypeVar, Any
from typing_extensions import Final

import attr
import cattr
from typing_extensions import Literal

TFileStrategies = Literal['backup', 'delete', 'warn', 'fail']
TSymlinkStrategies = Literal['replace', 'warn', 'fail']

VALID_FILE_STRATEGIES: Final[List[TFileStrategies]] = ['backup', 'delete', 'warn', 'fail']
VALID_SYMLINK_STRATEGIES: Final[List[TSymlinkStrategies]] = ['replace', 'warn', 'fail']

T = TypeVar('T')

def _literal_value_assertion(valid: List[T], obj: Any) -> T:
  if obj in valid:
    return cast(T, obj)
  else:
    raise ValueError(f"{obj} is not a valid value: {valid!r}")


_file_strategy_validator: Callable[[Any], T] = partial(_literal_value_assertion, VALID_FILE_STRATEGIES)
_symlink_strategy_validator: Callable[[Any], T] = partial(_literal_value_assertion, VALID_SYMLINK_STRATEGIES)


@attr.s(slots=True, frozen=True, auto_attribs=True)
class FileGroup:
  dirs: List[Path]
  """directories whose direct members will be added to the list of files to link"""

  globs: Optional[List[str]]
  """path globs that are relative to the base_dir that will be added to the list of files"""

  excludes: Optional[List[str]]
  """fnmatch globs that will be used to exclude items from the collected list"""

  target_dir: Path
  """an absolute path where the symlinks to this FileGroup's files will be created"""


@attr.s(slots=True, frozen=True, auto_attribs=True)
class Settings:
  """takes flags and creates a more high-level configuration object out of them"""
  conflicting_file_strategy: str = attr.ib()
  conflicting_symlink_strategy: str = attr.ib()

  @conflicting_file_strategy.validator
  def _validate_cfs(self, _ignore, value):
    _file_strategy_validator(value)

  @conflicting_symlink_strategy.validator
  def _validate_css(self, _ignore, value):
    _symlink_strategy_validator(value)

  base_dir: Path
  """the directory containing all of the files in this collection"""

  dotfiles_file_group: FileGroup
  binfiles_file_group: FileGroup

## register necessary serde with cattr

def _unstructure_path(posx: Path) -> str:
  return str(posx)


def _structure_path(pstr: str, typ: Type[Path]) -> Path:
  return Path(pstr)


cattr.register_structure_hook(Path, _structure_path)
cattr.register_unstructure_hook(Path, _unstructure_path)
