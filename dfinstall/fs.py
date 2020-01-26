import sys
import os
import os.path as osp
from stat import *
from pathlib import Path
import json


def handle_rename(p: Path):
  debug(f"handle_rename for p: {p}, p.exists: {p.exists()}")

  if p.exists():
    for n in range(0, 100):
      newp = p.with_suffix(f".{n:03}")
      if newp.exists():
        continue
      else:
        p.rename(newp)
        break
    else:
      raise RuntimeError(f"couln't find a suitable backup name for {p}")
  else:
    return None


def is_link(p: Path):
  try:
    s = os.lstat(p)
    return S_ISLNK(s.st_mode)
  except FileNotFoundError as e:
    return None


def anything_exists_at(p: Path):
  try:
    os.lstat(p)
    return True
  except FileNotFoundError:
    return False


def chase_links(link: Path):
  cur = link
  depth = 0
  while depth <= 50:
    depth += 1
    if not is_link(cur):
      return cur
    cur = osp.normpath(osp.join(cur.parent, os.readlink(cur)))
  else:
    raise RuntimeError(f"stack level too deep, couldn't find {link} after {depth} tries")


def link_points_to(link: Path, target: Path):
  # result = chase_links(link)

  try:
    data = os.readlink(link)
    return osp.samefile(chase_links(link), target)
  except FileNotFoundError:
    pass


def do_the_symlinking(top_dir, dotfiles=DOTFILES):
  for df in dotfiles:
    # the thing the link will point *to*
    target = Path(top_dir) / df

    # the location of the link itself
    link_path = (top_dir / '..' / f".{target.name}")

    # the data the link will contain
    link_data = target.relative_to(link_path.parent.resolve())

    def fn():
      if not os.path.lexists(link_path):
        link_path.symlink_to(link_data)  # ok, we're clear, do it

      elif is_link(link_path):
        debug(f"{link_path} is symlink")

        if link_points_to(link_path, target):
          debug(f"{link_path} resolves to {target}")
          return  # ok, we already did this, so skip it
        else:
          debug(f"{link_path} points to {os.readlink(link_path)}, remove it")
          os.unlink(link_path)  # link points somewhere dumb, remove it and run again
          return fn()  # recurse

      elif link_path.is_file() or link_path.is_dir():
        handle_rename(link_path)  # link path needs to be moved out of the way
        return fn()  # and recurse

      else:  # what the what?
        raise RuntimeError(f"{link_path} is not a file or symlink or directory, bailing")

    fn()
