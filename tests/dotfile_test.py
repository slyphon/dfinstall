from pathlib import Path

import pytest

from dfi.dotfile import find_common_root, LinkData


def test_find_common_root():
  a, b = Path("/path/to/a/b/c/d"), Path("/path/to/z/y/x/w/v")
  assert find_common_root(a, b) == Path("/path/to")

  a, b = Path("/one/two/three"), Path("/a/b/c")
  assert find_common_root(a, b) is None

  with pytest.raises(ValueError):
    find_common_root(Path("a/b/c"), Path("/a/b/c"))

  with pytest.raises(ValueError):
    find_common_root(Path("/a/b/c"), Path("a/b/c"))


def test_BinLinkData_relative():
  vpath = Path("/Users/foo/.settings/bin/bar")
  target_dir = Path("/Users/foo/.local/bin")

  bld = LinkData.for_path(vpath, target_dir)

  assert bld.link_path == Path("/Users/foo/.local/bin/bar")
  assert bld.link_data == Path("../../.settings/bin/bar")
