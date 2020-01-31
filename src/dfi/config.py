from functools import partial
from itertools import chain
from pathlib import Path
from typing import (Any, Callable, Dict, Iterable, List, Optional, Type, TypeVar, cast, Union)

from more_itertools import collapse

import attr
import cattr
from typing_extensions import Final, Literal

from . import dotfile
from .backports import cached_property
from .dotfile import LinkData

TSymlinkStrategy = Literal['replace', 'warn', 'fail']
TFileStrategy = Union[Literal['backup'], TSymlinkStrategy]

VALID_FILE_STRATEGIES: Final[List[TFileStrategy]] = ['backup', 'replace', 'warn', 'fail']
VALID_SYMLINK_STRATEGIES: Final[List[TSymlinkStrategy]] = ['replace', 'warn', 'fail']

T = TypeVar('T')


def _literal_value_assertion(valid: List[T], obj: Any) -> T:
  if obj in valid:
    return cast(T, obj)
  else:
    raise ValueError(f"{obj!r} is not a valid value: {valid!r}")


def ensure_is_file_strategy(any: Any) -> TFileStrategy:
  return _literal_value_assertion(VALID_FILE_STRATEGIES, any)


def ensure_is_symlink_strategy(any: Any) -> TSymlinkStrategy:
  return _literal_value_assertion(VALID_SYMLINK_STRATEGIES, any)


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

  @globs.validator
  def __glob_validator(
    self, _ignored: 'attr.Attribute[FileGroup]', value: Optional[List[str]]
  ) -> None:
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
  def _link_data_raw(self) -> List[LinkData]:
    return [LinkData.for_path(vpath, self.target_dir, self.link_prefix) for vpath in self.vpaths]

  @property
  def link_data(self) -> List[LinkData]:
    """LinkData for this FileGroup that contains no duplicate destinations

    The first entry in _link_data_raw wins based on link_path name
    """
    d: Dict[str, LinkData] = {}
    for ld in self._link_data_raw:
      if ld.link_path.name not in d:
        d[ld.link_path.name] = ld

    return [v for k, v in sorted(d.items())]

  @classmethod
  def _defaults(
    cls, base_dir: Path, target_dir: Path, dirs: List[Path], prefix: str
  ) -> 'FileGroup':
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

  file_groups: List[FileGroup]

  conflicting_file_strategy: str = attr.ib(default='backup')
  conflicting_symlink_strategy: str = attr.ib(default='replace')
  create_missing_target_dirs: bool = attr.ib(default=True)

  @conflicting_file_strategy.validator
  def __validate_cfs(self, _ignore: 'attr.Attribute[str]', value: str) -> None:
    ensure_is_file_strategy(value)

  @conflicting_symlink_strategy.validator
  def __validate_css(self, _ignore: 'attr.Attribute[str]', value: str) -> None:
    ensure_is_symlink_strategy(value)

  @classmethod
  def mk_default(cls, base_dir: Path) -> 'Settings':
    return cls(
      base_dir=base_dir,
      file_groups=[
        FileGroup.dotfile(base_dir),
        FileGroup.binfile(base_dir)
      ]
    )

  @property
  def vpaths(self) -> List[Path]:
    return list(collapse((fg.vpaths for fg in self.file_groups), base_type=FileGroup))

  @property
  def link_data(self) -> List[LinkData]:
    return list(collapse((fg.link_data for fg in self.file_groups), base_type=LinkData))


## register necessary serde with cattr


def _unstructure_path(posx: Path) -> str:
  return str(posx)


def _structure_path(pstr: str, typ: Type[Path]) -> Path:
  return Path(pstr)


# mypy: no-disallow-untyped-calls
cattr.register_structure_hook(Path, _structure_path)
cattr.register_unstructure_hook(Path, _unstructure_path)
