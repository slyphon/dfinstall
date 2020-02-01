import os.path
from pathlib import Path
from typing import Optional, Any

from marshmallow import Schema, fields, ValidationError
from marshmallow.fields import Field
from marshmallow.validate import OneOf


from .config import VALID_FILE_STRATEGIES, VALID_SYMLINK_STRATEGIES

def expandpath(p: Path) -> Path:
  return Path(os.path.expanduser(os.path.expandvars(p)))


class PathField(Field):
  def _serialize(self, value: Any, attr: Any, obj: Any, **kwargs: Any) -> Optional[str]:
    if value is None:
      return None
    elif isinstance(value, str):
      return value
    elif isinstance(value, Path):
      return str(Path)
    else:
      raise ValueError(f"could not serialize value {value!r}, attr: {attr!r}, obj: {obj!r}, kwargs: {kwargs!r}")

  def _deserialize(self, value: Any, attr: Any, data: Any, **kwargs: Any) -> Optional[Path]:
    if value is None:
      return None
    elif isinstance(value, str):
      return expandpath(Path(value))
    elif isinstance(value, Path):
      return expandpath(value)
    else:
      raise ValueError(f"could not deserialize value {value!r}, attr: {attr!r}, kwargs: {kwargs!r}")


class Defaults(Schema):
  conflicting_file_strategy = fields.String(
    validate=OneOf(VALID_FILE_STRATEGIES),
    default='backup',
  )

  conflicting_symlink_strategy = fields.String(
    validate=OneOf(VALID_SYMLINK_STRATEGIES),
    default='replace',
  )

  base_dir = PathField(default=Path.cwd)
  link_prefix = fields.String(default='')
  excludes = fields.List(fields.String(), default=lambda: ['.*'])

