import logging
from functools import partial
from itertools import chain, filterfalse
from pathlib import Path
from typing import Callable, Iterable, List, Optional, TypeVar, cast

import attr
from more_itertools import collapse

log = logging.getLogger(__name__)


@attr.s(slots=True, frozen=True, auto_attribs=True)
class Dotfile:
  # the "versioned" file, kept in source control
  # to which the link will point
  vpath: Path

  # the path of the symlink itself
  link_path: Path

  # the contents of the symlink
  link_data: Path

# %%
def collect(base_dir: Path, dirs: List[Path], globs: Optional[List[str]] = None, excludes: Optional[List[str]] = None) -> List[Path]:
  globs = globs if globs is not None else []
  exc = excludes if excludes is not None else []

  # collect dirents in dotfile_dirs
  dirents = chain(x.iterdir() for x in (base_dir.joinpath(dfd) for dfd in dirs))

  # collect globs relative to basedir in dotfiles
  globbed = chain(base_dir.glob(g) for g in globs)

  def any_excludes_match(p: Path) -> bool:
    return any(p.match(x) for x in exc)

  paths = collapse(chain(dirents, globbed), base_type=Path)

  return sorted(
    list(
      (x for x in paths if not any_excludes_match(x) and x.exists())
    )
  )


_ROOT = Path('/')

def _assert_is_absolute(a: Path):
  if not a.is_absolute():
    raise ValueError(f"argument must be an absolute Path, got {a}")

def find_common_root(a: Path, b: Path) -> Optional[Path]:
  _assert_is_absolute(a)
  _assert_is_absolute(b)

  while True:
    log.debug(f"a: {a}, b: {b}")
    if a == _ROOT or b == _ROOT:
      return None
    elif a == b:
      return a
    elif len(a.parts) > len(b.parts):
      a = a.parent
    elif len(a.parts) < len(b.parts):
      b = b.parent
    else:
      a, b = a.parent, b.parent


# %%
