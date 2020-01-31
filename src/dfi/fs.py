from typing import List, Optional, Union, cast, Dict, Callable
import sys
import os
import os.path as osp
from stat import *
from pathlib import Path
import json
import logging

import arrow
from .dotfile import LinkData
from .config import Settings, TFileStrategy, TSymlinkStrategy, file_strategy_validator, symlink_strategy_validator
from .exceptions import (BackupFailed, TooManySymbolicLinks, FatalConflict, FilesystemConflictError)

log = logging.getLogger(__name__)

_DATE_FORMAT_STR = 'YYYYMMDDHHmmss'


class _skipConflictingEntry(Exception):
  pass


def skip_it() -> None:
  raise _skipConflictingEntry()


def timestamp() -> str:
  return cast(str, arrow.utcnow().format(_DATE_FORMAT_STR))


def backup(p: Path) -> Optional[Path]:
  log.debug(f"handle rename for p: {p}, p.exists: {p.exists()}")

  if p.exists():
    for n in range(0, 100):
      newp = p.with_suffix(f".dfi_{timestamp()}_{n:03}")
      if newp.exists():
        log.debug(f"backup path {newp!s} existed, retrying")
        continue
      else:
        p.rename(newp)
        return newp
    else:
      raise BackupFailed(p)
  else:
    return None


def is_link(p: Path) -> Optional[bool]:
  try:
    s = os.lstat(p)
    return S_ISLNK(s.st_mode)
  except FileNotFoundError:
    return None


def chase_links(link: Path) -> Path:
  cur = link
  depth = 0
  while depth <= 50:
    depth += 1
    if not is_link(cur):
      return cur
    cur = Path(osp.normpath(osp.join(cur.parent, os.readlink(cur))))
  else:
    raise TooManySymbolicLinks(link, depth)


def link_points_to(link: Path, target: Path) -> Optional[bool]:
  try:
    data = os.readlink(link)
    return osp.samefile(chase_links(link), target)
  except FileNotFoundError:
    return None


def backup_file_strategy(p: Path) -> None:
  """when a link_path exists and is a file, this method moves it to a unique location"""
  log.debug(f"backup_file_strategy: {p}")
  backup(p)


def delete_strategy(p: Path) -> None:
  """when a link_path exists and is a file, this method removes it"""
  log.debug(f"delete_strategy: {p}")
  p.unlink()


def warn_strategy(p: Path) -> None:
  log.warning(f"File location {str(p)!r} already exists and 'warn' strategy selected, continuing.")
  skip_it()


def fail_strategy(p: Path) -> None:
  raise FatalConflict(p)


StrategyFn = Callable[[Path], None]

_FILE_STRATEGY_MAP: Dict[TFileStrategy, StrategyFn] = {
  'backup': backup_file_strategy,
  'delete': delete_strategy,
  'warn': warn_strategy,
  'fail': fail_strategy,
}

_SYMLINK_STRATEGY_MAP: Dict[TSymlinkStrategy, StrategyFn] = {
  'replace': delete_strategy,
  'warn': warn_strategy,
  'fail': fail_strategy,
}


def _apply_link_data(
  ld: LinkData, create_missing: bool, file_stgy: StrategyFn, link_stgy: StrategyFn
) -> None:
  target, link_data, link_path = ld.vpath, ld.link_data, ld.link_path

  # TODO: make this a setting
  if not link_path.parent.exists():
    link_path.parent.mkdir(mode=0o755, parents=True, exist_ok=True)

  def fn() -> None:
    # os.path.exists reports false for a broken symlink
    if not os.path.exists(link_path) or is_link(link_path):

      if not is_link(link_path):
        link_path.symlink_to(link_data)  # ok, we're clear, do it
        return

      log.debug(f"{link_path} is symlink")

      if link_points_to(link_path, target):
        log.debug(f"{link_path} resolves to {target}")
        return  # ok, we already did this, so skip it
      else:
        log.debug(f"{link_path} points to {os.readlink(link_path)}")
        link_stgy(link_path)
        return fn()  # recurse

    elif link_path.is_file() or link_path.is_dir():
      file_stgy(link_path)
      return fn()  # and recurse

    else:  # what the what?
      raise FilesystemConflictError(link_path, os.stat(link_path))

  try:
    fn()
  except _skipConflictingEntry as e:
    return None


def apply_link_data(
  link_datas: List[LinkData], create_missing: bool, fs: StrategyFn, ls: StrategyFn
) -> None:
  for ld in link_datas:
    _apply_link_data(ld, create_missing, fs, ls)


def apply_settings(settings: Settings) -> None:
  apply_link_data(
    settings.link_data,
    settings.create_missing_target_dirs,
    # revalidating here is silly, but it appeases mypy, because declaring
    # these as literal types on the Settings object messes up serialization
    _FILE_STRATEGY_MAP[file_strategy_validator(settings.conflicting_file_strategy)],
    _SYMLINK_STRATEGY_MAP[symlink_strategy_validator(settings.conflicting_symlink_strategy)]
  )
