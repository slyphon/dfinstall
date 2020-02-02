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

  @post_load
  def _mk_on_conflict(self, data: Dict[str, Any], **kw: Any) -> OnConflict:
    return OnConflict(**data)


OnConflictSchema = _OnConflict()


class _Defaults(Schema):
  on_conflict = fields.Nested(_OnConflict, missing=lambda: OnConflictSchema.load({}))
  base_dir = PathField(missing=Path.cwd)
  link_prefix = fields.String(missing='')
  excludes = fields.List(fields.String(), missing=lambda: ['.*'])


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

  @post_load
  def _mk_file_group(self, data: Dict[str, Any], **kw: Any) -> FileGroup:
    return FileGroup(**data)

FileGroupSchema = _FileGroup()


# mypy: allow-any-decorated
class _Settings(Schema):
  base_dir = PathField(required=True)
  file_groups = fields.List(fields.Nested(_FileGroup))
  on_conflict = fields.Nested(_OnConflict)

  @pre_load
  def _pre_load_settings(self, data: Dict[str, Any], **kw: Any) -> Dict[str, Any]:
    if 'on_conflict' in data:
      default_on_conflict = data['on_conflict']
    else:
      default_on_conflict = data['on_conflict'] = OnConflict()

    if 'file_groups' in data:
      for fgdict in data['file_groups']:
        if 'on_conflict' not in fgdict:
          fgdict.update(dict(on_conflict=default_on_conflict))

    return data



  @post_load
  def _mk_settings(self, data: Dict[str, Any], **kw: Dict[str, Any]) -> Settings:
    default_on_conflict: OnConflict

    if 'on_conflict' in data:
      default_on_conflict = data['on_conflict']
    else:
      default_on_conflict = data['on_conflict'] = OnConflict()

    if 'file_groups' in data:
      for fgdict in data['file_groups']:
        pass

    return Settings(**data)


SettingsSchema = _Settings()
