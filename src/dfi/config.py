from pathlib import Path
from functools import partial
from typing import Callable, Iterable, List, Optional, Type, cast, TypeVar, Any
from typing_extensions import Final
from itertools import chain

import attr
import cattr
from typing_extensions import Literal

from .backports import cached_property
from . import dotfile
from .dotfile import LinkData

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


_file_strategy_validator: Callable[[Any], T] = \
  partial(_literal_value_assertion, VALID_FILE_STRATEGIES)


_symlink_strategy_validator: Callable[[Any], T] = \
  partial(_literal_value_assertion, VALID_SYMLINK_STRATEGIES)

DEFAULT_EXCLUDES: Final[List[str]] = ['.*']


@attr.s(frozen=True, slots=True, auto_attribs=True)
class FileGroup:
  # the version-controlled directory that contains the files-to-symlink
  base_dir: Path

  # directories whose direct members will be added to the list of files to link
  dirs: List[Path]

  # path globs that are relative to the base_dir that will be added to the list of files
  globs: Optional[List[str]] = attr.ib()

  # fnmatch globs that will be used to exclude items from the collected list
  excludes: Optional[List[str]]

  # an absolute path where the symlinks to this FileGroup's files will be created
  target_dir: Path

  # the prefix to use for the link path (i.e. '.')
  link_prefix: str = attr.ib(default='')

  def evolve(self, **kw) -> 'FileGroup':
    return attr.evolve(self, **kw)

  @globs.validator
  def __glob_validator(self, _ignored, value):
    if value is None:
      return
    for v in value:
      if not isinstance(v, str):
        raise TypeError(f"globs must be strings, not {type(v)}, value: {v!r}")


  @property
  def vpaths(self) -> List[Path]:
    """return a collection of absolute source paths to be symlinked
    collects from both dirs and globs and applies the excludes before returning
    """
    return dotfile.collect(self.base_dir, self.dirs, self.globs, self.excludes)

  @property
  def link_data(self) -> List[LinkData]:
    return [LinkData.for_path(vpath, self.target_dir, self.link_prefix) for vpath in self.vpaths]

  @classmethod
  def _defaults(cls, base_dir: Path, target_dir: Path, dirs: List[Path], prefix: str) -> 'FileGroup':
    return cls(
      base_dir=base_dir,
      target_dir=target_dir,
      dirs=dirs,
      excludes=DEFAULT_EXCLUDES[:],
      globs=None,
      link_prefix=prefix,
    )

  @classmethod
  def dotfile(cls, base_dir: Path) -> 'FileGroup':
    """default config for dotfiles"""
    return cls._defaults(
      base_dir=base_dir,
      target_dir=base_dir.parent,
      dirs=[Path('dotfiles')],
      prefix='.',
    )

  @classmethod
  def binfile(cls, base_dir: Path) -> 'FileGroup':
    """default config for binfiles"""
    return cls._defaults(
      base_dir=base_dir,
      target_dir=base_dir.parent.joinpath(".local", "bin"),
      dirs=[Path('bin')],
      prefix='',
    )

class EmptyFileGroup(FileGroup):
  @property
  def vpaths(self) -> List[Path]:
    return []


@attr.s(auto_attribs=True)
class Settings:
  """takes flags and creates a more high-level configuration object out of them"""

  base_dir: Path
  """the directory containing all of the files in this collection"""

  dotfiles_file_group: FileGroup
  binfiles_file_group: FileGroup

  conflicting_file_strategy: str = attr.ib(default='backup')
  conflicting_symlink_strategy: str = attr.ib(default='replace')

  @conflicting_file_strategy.validator
  def __validate_cfs(self, _ignore, value):
    _file_strategy_validator(value)

  @conflicting_symlink_strategy.validator
  def __validate_css(self, _ignore, value):
    _symlink_strategy_validator(value)

  def evolve(self, **kw) -> 'Settings':
    return attr.evolve(self, **kw)

  @classmethod
  def mk_default(cls, base_dir: Path) -> 'Settings':
    return cls(
      base_dir=base_dir,
      dotfiles_file_group=FileGroup.dotfile(base_dir),
      binfiles_file_group=FileGroup.binfile(base_dir),
    )

  @property
  def vpaths(self) -> List[Path]:
    return list(chain(self.binfiles_file_group.vpaths, self.dotfiles_file_group.vpaths))

  @property
  def link_data(self) -> List[LinkData]:
    return list(chain(self.binfiles_file_group.link_data, self.dotfiles_file_group.link_data))

## register necessary serde with cattr


def _unstructure_path(posx: Path) -> str:
  return str(posx)


def _structure_path(pstr: str, typ: Type[Path]) -> Path:
  return Path(pstr)


cattr.register_structure_hook(Path, _structure_path)
cattr.register_unstructure_hook(Path, _unstructure_path)
