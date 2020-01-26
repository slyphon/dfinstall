from dynaconf import LazySettings

# settings can be overridden by using environment variables
# DFINSTALL_BLAH to override the 'BLAH' setting.
ENVVAR_PREFIX_FOR_DYNACONF = 'DFINSTALL'

# this env var controls what settings 'environment' we load
ENV_SWITCHER_FOR_DYNACONF='DFINSTALL_ENV'

# env var that points to where the settings file lives
ENVVAR_FOR_DYNACONF = "DFINSTALL_SETTINGS"

settings = LazySettings(
  ENVVAR_PREFIX_FOR_DYNACONF=ENVVAR_PREFIX_FOR_DYNACONF,
  ENVVAR_FOR_DYNACONF=ENVVAR_FOR_DYNACONF,
  ENV_SWITCHER_FOR_DYNACONF=ENV_SWITCHER_FOR_DYNACONF,
)
