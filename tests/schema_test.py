import os
from pathlib import Path
from pprint import pprint
from typing import Any, Dict

import pytest

from dotmap import DotMap
from marshmallow import Schema
from marshmallow.exceptions import ValidationError
from py._code.code import ExceptionInfo

from dfi.config import OnConflict, Settings
from dfi.schema import (Defaults, FileGroupSchema, OnConflictSchema, PathField, SettingsSchema, EnvSection)

from .conftest import chdir

ON_CONFLICT = dict(file='replace', symlink='fail')


class P(Schema):
  path = PathField(required=True)


def test_PathField_dump():
  d = P().dump(dict(path=Path("a/b/c")))
  assert DotMap(d).path == "a/b/c"


def test_Defaults_basic(tmp_path: Path):
  with chdir(tmp_path):
    d = Defaults.load(dict())

    assert d == dict(
      on_conflict=dict(
        file='backup',
        symlink='replace',
      ),
      base_dir=tmp_path,
      link_prefix='',
      excludes=[],
    )


def test_unknown_field():
  e: ExceptionInfo
  with pytest.raises(ValidationError) as e:
    d = Defaults.load(dict(conflicting_file_strategy='nope'))

  assert 'conflicting_file_strategy' in e.value.messages
  assert e.value.messages['conflicting_file_strategy'][0] == "Unknown field."


def test_on_conflict_file_validation():
  e: ExceptionInfo
  with pytest.raises(ValidationError) as e:
    d = Defaults.load({'on_conflict': {'file': 'boo'}})

  dm = DotMap(e.value.messages)

  assert dm.on_conflict.file[0].startswith("Must be one of:")


def test_on_conflict_symlink_validation():
  e: ExceptionInfo
  with pytest.raises(ValidationError) as e:
    d = Defaults.load({'on_conflict': {'symlink': 'boo'}})

  dm = DotMap(e.value.messages)

  assert dm.on_conflict.symlink[0].startswith("Must be one of:")


@pytest.fixture()
def fg_defaults() -> Dict[str, Any]:
  return dict(
    base_dir=Path.cwd().joinpath('settings'),
    dirs=[Path('dotfiles')],
    globs=['foo/*'],
    excludes=['.*', '*.bak'],
    target_dir=Path.cwd(),
    link_prefix='.',
    on_conflict=ON_CONFLICT,
  )


def test_file_group_schema_deserialize(tmp_path: Path, fg_defaults: Dict[str, Any]):
  with chdir(tmp_path):
    FileGroupSchema.load(fg_defaults)


def test_file_group_schema_validation_base_dir_required(fg_defaults: Dict[str, Any]):
  e: ExceptionInfo
  fg_defaults.pop('base_dir')
  fg_defaults.pop('target_dir')
  with pytest.raises(ValidationError) as e:
    FileGroupSchema.load(fg_defaults)

  dm = DotMap(e.value.messages)

  assert len(dm.base_dir) == 1
  assert len(dm.target_dir) == 1
  assert dm.base_dir[0] == 'Missing data for required field.'
  assert dm.target_dir[0] == 'Missing data for required field.'


@pytest.fixture()
def settings_defaults(fg_defaults):
  return dict(
    base_dir=os.getcwd(),
    file_groups=[
      dict(
        base_dir=str(Path.cwd().joinpath('settings')),
        dirs=['dotfiles'],
        globs=['foo/*'],
        excludes=['.*', '*.bak'],
        target_dir=str(Path.cwd()),
        link_prefix='.',
        create_missing_target=True,
      )
    ],
    on_conflict=ON_CONFLICT,
  )


def test_settings_schema(settings_defaults):
  stg = SettingsSchema.load(settings_defaults)
  dumped = SettingsSchema.dump(stg)
  assert dumped == settings_defaults


def test_EnvSection_schema(monkeypatch):
  monkeypatch.setenv("HOME", "/home/blah")

  fg = dict(
    base_dir="$HOME/.settings",
    dirs=['dotfiles'],
    globs=['foo/*'],
    excludes=['*.bak'],
    target_dir=str("~/target"),
    link_prefix='.',
    create_missing_target=True,
  )

  d = EnvSection.load(dict(file_groups=[fg]))
  fgs = d['file_groups']
  assert len(fgs) == 1
  fg: FileGroup = fgs[0]
  assert fg['base_dir'] == Path("/home/blah/.settings")
  assert fg['target_dir'] == Path("/home/blah/target")
