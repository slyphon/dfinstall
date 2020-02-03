import logging
import os
from functools import wraps
from itertools import chain
from pathlib import Path
from typing import (Any, Callable, Dict, Iterable, List, Optional, Type, TypeVar, Union, cast)

import attr
import toml
from more_itertools import collapse
from typing_extensions import Final, Literal

from . import dotfile
from .backports import cached_property
from .dotfile import LinkData
from .strategies import (
  VALID_FILE_STRATEGIES,
  VALID_SYMLINK_STRATEGIES,
  TFileStrategy,
  TSymlinkStrategy,
  ensure_is_file_strategy,
  ensure_is_symlink_strategy
)


log = logging.getLogger(__name__)

DEFAULT_EXCLUDES: Final[List[str]] = ['.*']


@attr.s(auto_attribs=True, cache_hash=True, frozen=True, kw_only=True, slots=True)
class OnConflict:
  file: TFileStrategy = attr.ib(default='backup')
  symlink: TSymlinkStrategy = attr.ib(default='replace')

  @file.validator
  def __validate_cfs(self, _ignore: 'attr.Attribute[str]', value: str) -> None:
    ensure_is_file_strategy(value)

  @symlink.validator
  def __validate_css(self, _ignore: 'attr.Attribute[str]', value: str) -> None:
    ensure_is_symlink_strategy(value)


@attr.s(frozen=True, slots=True, auto_attribs=True, kw_only=True, cache_hash=True)
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

  on_conflict: Optional[OnConflict] = attr.ib(default=None)

  # the prefix to use for the link path (i.e. '.')
  link_prefix: str = attr.ib(default='')

  # if a target directory doesn't exist should we mkdir -p it?
  create_missing_target: bool = attr.ib(default=True)

  @globs.validator
  def __glob_validator(
    self, _ignored: 'attr.Attribute[FileGroup]', value: Optional[List[str]]
  ) -> None:
    if value is None:
      return
    for v in value:
      if not isinstance(v, str):
        raise TypeError(f"globs must be strings, not {type(v)}, value: {v!r}")
      if '**' in v:
        raise ValueError(f"globs are evaluated non-recursively, {v!r} is an invalid pattern")

  @link_prefix.validator
  def __link_prefix_validator(self, _ignored: 'attr.Attribute[str]', value: str) -> None:
    if '/' in value:
      raise ValueError(f"link_prefix argument may not contain '/': {value!r}")

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
      on_conflict=OnConflict(),
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


def _convert_file_group(fg: List[Union[FileGroup, Dict[str, Any]]]) -> List[FileGroup]:
  def one(f: Union[FileGroup, Dict[str, Any]]) -> FileGroup:
    if isinstance(f, FileGroup):
      return f
    else:
      return FileGroup(**f)

  return [one(f) for f in fg]


def _convert_on_conflict(oc: Union[OnConflict, Dict[str, Any]]) -> OnConflict:
  if isinstance(oc, OnConflict):
    return oc
  else:
    return OnConflict(**oc)


@attr.s(auto_attribs=True, frozen=True, slots=True, kw_only=True, cache_hash=True)
class Settings:
  """takes flags and creates a more high-level configuration object out of them"""

  # the directory containing all of the files in this collection
  base_dir: Path

  file_groups: List[FileGroup] = attr.ib(converter=_convert_file_group)

  # the default on_conflict setting
  on_conflict: OnConflict = attr.ib(converter=_convert_on_conflict)

  @on_conflict.default
  def _on_conflict_default(self) -> OnConflict:
    return OnConflict()

  @classmethod
  def mk_default(cls, base_dir: Path) -> 'Settings':
    return cls(
      base_dir=base_dir, file_groups=[FileGroup.dotfile(base_dir), FileGroup.binfile(base_dir)]
    )

  @property
  def vpaths(self) -> List[Path]:
    return list(collapse((fg.vpaths for fg in self.file_groups), base_type=FileGroup))

  @property
  def link_data(self) -> List[LinkData]:
    return list(collapse((fg.link_data for fg in self.file_groups), base_type=LinkData))
