from pathlib import Path
import attr

@attr.s(slots=True, frozen=True, auto_attribs=True)
class Dotfile:
  # the "versioned" file, kept in source control
  # to which the link will point
  vpath: Path

  # the path of the symlink itself
  link_path: Path

  # the contents of the symlink
  link_data: Path


