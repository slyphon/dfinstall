import logging
from functools import partial
from itertools import chain, filterfalse
from pathlib import Path
from typing import Callable, Iterable, List, Optional, TypeVar, cast
from typing_extensions import Final

import attr
from more_itertools import collapse

log = logging.getLogger(__name__)


@attr.s(slots=True, frozen=True, auto_attribs=True)
class LinkData:
  # the "versioned" file, kept in source control to which the link will point
  vpath: Path
  # the path of the symlink itself
  link_path: Path
  # the contents of the symlink
  link_data: Path

  @classmethod
  def for_path(cls, vpath: Path, target_dir: Path, prefix: str = '') -> 'LinkData':
    link_path = target_dir.joinpath(prefix + vpath.name)
    # calculate the common root between the vpath and the link_path
    #
    # vpath = '/Users/foo/settings/bin/thing'
    # link_path = '/Users/foo/.local/bin/thing'
    # find_common_root(vpath, link_path)
    # >>> PosixPath('/Users/foo')
    #
    common = find_common_root(vpath, link_path)
    if common is not None:
      # calculate the number of '..' we need to get to the common root
      nup = len(link_path.parent.parts) - len(common.parts)
      # so if we make a symlink at link_path, to refer to the vpath we need nup '..' entries
      # to get us to the common ancestor. then we add the relative path to the vpath from
      # the common directory.
      #
      # so in the example above the link data should be '../../settings/bin/thing'
      #
      link_data = Path(*['..' for n in range(0, nup)]) / vpath.relative_to(common)
      return cls(vpath=vpath, link_path=link_path, link_data=link_data)
    else:
      # otherwise, without a common root, we just use the abspath
      return cls(vpath=vpath, link_path=link_path, link_data=vpath)



# %%
def collect(
  base_dir: Path,
  dirs: List[Path],
  globs: Optional[List[str]] = None,
  excludes: Optional[List[str]] = None
) -> List[Path]:
  globs = globs if globs is not None else []
  exc = excludes if excludes is not None else []

  # collect dirents in dotfile_dirs
  dirents = chain(x.iterdir() for x in (base_dir.joinpath(dfd) for dfd in dirs))

  # collect globs relative to basedir in dotfiles
  globbed = chain(base_dir.glob(g) for g in globs)

  def any_excludes_match(p: Path) -> bool:
    return any(p.match(x) for x in exc)

  paths = collapse(chain(dirents, globbed), base_type=Path)

  cleaned = [x for x in paths if not any_excludes_match(x) and x.exists()]

  return sorted(cleaned)


_ROOT = Path('/')


def _assert_is_absolute(a: Path) -> None:
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
