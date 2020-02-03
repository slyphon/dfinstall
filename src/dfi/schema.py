import logging
import os.path
from pathlib import Path
from typing import Any, Callable, Dict, Optional, TypeVar, cast

from marshmallow import Schema, ValidationError, fields, post_load, pre_load
from marshmallow.fields import Field
from marshmallow.validate import OneOf

from .config import FileGroup, OnConflict, Settings
from .strategies import VALID_FILE_STRATEGIES, VALID_SYMLINK_STRATEGIES

log = logging.getLogger(__name__)


def expandpath(p: Path) -> Path:
  return Path(os.path.expanduser(os.path.expandvars(p)))


class PathField(Field):
  def _serialize(self, value: Any, attr: Any, obj: Any, **kwargs: Any) -> Optional[str]:
    if value is None:
      return None
    elif isinstance(value, str):
      return value
    elif isinstance(value, Path):
      return str(value)
    else:
      raise ValueError(
        f"could not serialize value {value!r}, attr: {attr!r}, obj: {obj!r}, kwargs: {kwargs!r}"
      )

  def _deserialize(self, value: Any, attr: Any, data: Any, **kwargs: Any) -> Optional[Path]:
    if value is None:
      return None
    elif isinstance(value, str):
      return expandpath(Path(value))
    elif isinstance(value, Path):
      return expandpath(value)
    else:
      raise ValueError(f"could not deserialize value {value!r}, attr: {attr!r}, kwargs: {kwargs!r}")


class _OnConflict(Schema):
  file = fields.String(
    validate=OneOf(VALID_FILE_STRATEGIES),
    missing='backup',
  )

  symlink = fields.String(
    validate=OneOf(VALID_SYMLINK_STRATEGIES),
    missing='replace',
  )


OnConflictSchema = _OnConflict()


class _OnConflictFactory(_OnConflict):
  @post_load
  def _mk_on_conflict(self, data: Dict[str, Any], **kw: Any) -> OnConflict:
    return OnConflict(**data)


OnConflictFactory = _OnConflictFactory()


class _Defaults(Schema):
  on_conflict = fields.Nested(_OnConflict, missing=lambda: OnConflictSchema.load({}))
  base_dir = PathField(missing=Path.cwd)
  link_prefix = fields.String(missing='')
  excludes = fields.List(fields.String(), missing=list, default=list)


Defaults = _Defaults()


class _FileGroup(Schema):
  base_dir = PathField(required=True)
  dirs = fields.List(PathField, missing=list)
  globs = fields.List(fields.String, missing=list)
  excludes = fields.List(fields.String, missing=list)
  target_dir = PathField(required=True)
  link_prefix = fields.String(missing='')
  create_missing_target = fields.Bool(default=True)
  on_conflict = fields.Nested(_OnConflict)


FileGroupSchema = _FileGroup()


class _FileGroupFactory(_FileGroup):
  @post_load
  def _mk_file_group(self, data: Dict[str, Any], **kw: Any) -> FileGroup:
    if 'on_conflict' in data and isinstance(data['on_conflict'], dict):
      data['on_conflict'] = OnConflict(**data['on_conflict'])
    return FileGroup(**data)


FileGroupFactory = _FileGroupFactory()


class _EnvSection(Schema):
  file_groups = fields.List(fields.Nested(_FileGroup))


EnvSection = _EnvSection()


# mypy: allow-any-decorated
class _Settings(Schema):
  base_dir = PathField(required=True)
  file_groups = fields.List(fields.Nested(_FileGroup))
  on_conflict = fields.Nested(_OnConflict)


SettingsSchema = _Settings()


class _SettingsFactory(_Settings):
  """this is equivalent to _Settings but it returns a Settings struct after validation"""

  @post_load
  def _mk_settings(self, data: Dict[str, Any], **kw: Dict[str, Any]) -> Settings:
    if 'file_groups' in data:
      data['file_groups'] = [FileGroupFactory.load(fgdict) for fgdict in data['file_groups']]

    return Settings(**data)


SettingsFactory = _SettingsFactory()
