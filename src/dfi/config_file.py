"""
utilities for loading the config file and applying defaults
"""

import os
from pathlib import Path
from typing import Dict, TypeVar, cast, Any, TextIO, Union
from copy import deepcopy

import toml
from dotmap import DotMap
from deepmerge import always_merger

from .config import Settings
from .exceptions import EnvNotFoundError
from .schema import Defaults, EnvSection, FileGroupSchema, SettingsFactory

_K = TypeVar('_K')
_V = TypeVar('_V')

def _merge_under(defaults: Dict[_K, _V], target: Dict[_K, _V]) -> Dict[_K, _V]:
  d = deepcopy(defaults)
  t = deepcopy(target)
  return cast(Dict[_K, _V], always_merger.merge(d, t))

def _load_and_apply_defaults(fp: TextIO, env_name: str) -> Dict[str, Any]:
  raw = toml.load(fp)
  dflt = Defaults.load(raw.get('default', {}), partial=True)

  env_section = raw.get(env_name, None)

  if 'file_groups' in env_section:
    for i, fg in enumerate(env_section['file_groups']):
      env_section['file_groups'][i] = _merge_under(dflt, fg)

  es = EnvSection.load(env_section)
  return _merge_under(dflt, es)

def load(input: Union[Path, TextIO], env: str) -> Settings:
  data: Dict[str, Any]

  if isinstance(input, Path):
    with input.open(mode='r', encoding='utf8') as fp:
      data = _load_and_apply_defaults(fp, env)
  else:
    data = _load_and_apply_defaults(input, env)

  return cast(Settings, SettingsFactory.load(data))
