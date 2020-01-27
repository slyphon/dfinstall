from pathlib import Path

from dfinstall.dotfile import find_common_root

def test_find_common_root():
  a, b = Path("/path/to/a/b/c/d"), Path("/path/to/z/y/x/w/v")
  assert find_common_root(a, b) == Path("/path/to")

  a, b = Path("/one/two/three"), Path("/a/b/c")
  assert find_common_root(a, b) is None

