import os
from typing import Optional, Sequence, Any
from pathlib import Path
from .dotfile import LinkData

class DFIError(Exception):
  """root of all application generated errors"""
  def __init__(self, *a: Sequence[Any]) -> None:
    super().__init__(*a)

class FilesystemConflictError(DFIError):
  """this exception is thrown when a conflict happens and we
  don't know how to resolve it based on the type of conflicting
  object (i.e. a fifo, device, etc.)
  """
  def __init__(self, path: Path, stat: os.stat_result, *a: Sequence[Any]) -> None:
    args = [f"Unresolvable conflict at {path}, stat: {stat!r}", *a]
    super().__init__(*args)

class BackupFailed(DFIError):
  """raised when we couldn't find a suitable backup name for the backup strategy"""
  def __init__(self, path: Path, *a: Sequence[Any]) -> None:
    args = [f"Failed to back up conflicting target path {str(path)}", *a]
    super().__init__(*args)

class TooManySymbolicLinks(DFIError):
  """raised when we try to resolve a symlink and find a loop"""
  def __init__(self, link: Path, depth: int, *a: Sequence[Any]) -> None:
    args = [f"Too many symbolic links encountered (> {depth}) trying to read conflicting target path {link}", *a]
    super().__init__(*args)

class FatalConflict(DFIError):
  """raised when the config is to 'fail' for a conflict"""
  def __init__(self, path: Path, *a: Sequence[Any]) -> None:
    args = [f"Conflict at path {path} and 'fail' selected as resolution strategy", *a]
    super().__init__(*args)
