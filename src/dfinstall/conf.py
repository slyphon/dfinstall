from pathlib import Path

from dynaconf import LazySettings, Validator

DEFAULTS = dict(
  ENVVAR_PREFIX_FOR_DYNACONF='DFINSTALL',
  ENVVAR_FOR_DYNACONF="DFINSTALL_SETTINGS",
  ENV_SWITCHER_FOR_DYNACONF='DFINSTALL_ENV',
  DEBUG_LEVEL_FOR_DYNACONF='DEBUG',
)

VALID_FILE_STRATEGIES = ['backup', 'delete', 'warn', 'fail']
VALID_SYMLINK_STRATEGIES = ['replace', 'warn', 'fail']

def valid_dest_dir(value: str) -> bool:
  pv = Path(value)
  return value == '%CWD_PARENT%' or pv.is_absolute() and pv.exists() and pv.is_dir()

def mk_settings(**kw) -> LazySettings:
  dflt = dict(**DEFAULTS)
  dflt.update(kw)

  settings = LazySettings(**dflt)

  settings.validators.register(
    Validator('CONFLICTING_FILE_STRATEGY', must_exist=True, is_in=VALID_FILE_STRATEGIES),
    Validator('CONFLICTING_SYMLINK_STRATEGY', must_exist=True, is_in=VALID_SYMLINK_STRATEGIES),
    Validator('DEST_DIR', must_exist=True, condition=valid_dest_dir)
  )

  return settings
