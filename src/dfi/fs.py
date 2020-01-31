from typing import List, Optional, Union, cast
import sys
import os
import os.path as osp
from stat import *
from pathlib import Path
import json
import logging

import arrow
from .dotfile import LinkData
from .config import Settings

log = logging.getLogger(__name__)

_DATE_FORMAT_STR = 'YYYYMMDDHHmmss'


def timestamp() -> str:
  return cast(str, arrow.utcnow().format(_DATE_FORMAT_STR))


def backup(p: Path) -> Optional[Path]:
  log.debug(f"handle_rename for p: {p}, p.exists: {p.exists()}")

  if p.exists():
    for n in range(0, 100):
      newp = p.with_suffix(f"dfi_{timestamp()}_{n:03}")
      if newp.exists():
        continue
      else:
        p.rename(newp)
        return newp
    else:
      raise RuntimeError(f"couln't find a suitable backup name for {p}")
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
    raise RuntimeError(f"stack level too deep, couldn't find {link} after {depth} tries")


def link_points_to(link: Path, target: Path) -> Optional[bool]:
  try:
    data = os.readlink(link)
    return osp.samefile(chase_links(link), target)
  except FileNotFoundError:
    return None


def _apply_link_data(ld: LinkData, create_missing: bool) -> None:
  target, link_data, link_path = ld.vpath, ld.link_data, ld.link_path

  if not link_path.parent.exists():
    link_path.parent.mkdir(mode=0o755, parents=True, exist_ok=True)

  def fn() -> None:
    if not os.path.exists(link_path):
      link_path.symlink_to(link_data) #ok, we're clear, do it

    elif is_link(link_path):
      log.debug(f"{link_path} is symlink")

      if link_points_to(link_path, target):
        log.debug(f"{link_path} resolves to {target}")
        return  # ok, we already did this, so skip it
      else:
        log.debug(f"{link_path} points to {os.readlink(link_path)}, remove it")
        os.unlink(link_path)  # link points somewhere dumb, remove it and run again
        return fn()  # recurse

    elif link_path.is_file() or link_path.is_dir():
      backup(link_path)  # link path needs to be moved out of the way
      return fn()  # and recurse

    else:  # what the what?
      raise RuntimeError(f"{link_path} is not a file or symlink or directory, bailing")

  fn()


def apply_link_data(link_datas: List[LinkData], create_missing: bool) -> None:
  for ld in link_datas:
    _apply_link_data(ld, create_missing)

def apply_settings(settings: Settings) -> None:
  apply_link_data(settings.link_data, settings.create_missing_target_dirs)
