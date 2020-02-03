import json
import os
import os.path  # type: ignore # noqa
from pathlib import Path
from pprint import pprint
from typing import List, Optional, TextIO
from textwrap import dedent

import attr
import cattr
import click
from dotenv import find_dotenv, load_dotenv

from . import fs
from .click_ext import PATHSEP_STRING
from . import config_file as _config_file_mod
from .config import FileGroup, OnConflict, Settings
from .schema import SettingsFactory


def _strip_help(text: str) -> str:
  return dedent(text).replace("\n", " ").rstrip()

# mypy: allow-untyped-decorators
@click.command()
@click.option(
  '--dump-settings',
  help="""dumps a configuration in json that matches the flags given to the path provided (or stdout for -) and exits""",
  type=click.File(mode='w', encoding='utf8'), # type: ignore
  hidden=True,
)
@click.option(
  "-p", "--profile",
  default='standard',
  allow_from_autoenv=True,
  show_envvar=True,
  help=_strip_help("""\
    The profile to load from the config file. Should be the name
    of a configuration key that defines at least one file_group to create
    symlinks for. Can also be set with the DFI_PROFILE environment variable.
    If this option is not set, the 'standard' profile will be used. See the
    main help for an explanation of the standard profile.
    """),
)
@click.option(
  '-f', '--config-file',
  help=_strip_help("""\
    path to the config file to use, by default use "dfi.toml" in the current directory.
    Can also be set using the DFI_CONFIG_FILE environment variable
  """),
  type=click.File(mode='r', encoding='utf8'),
  default='dfi.toml',
  envvar='DFI_CONFIG_FILE',
)
def main(
  config_file: TextIO,
  profile: str,
  dump_settings: Optional[TextIO]
) -> None:
  """\
    The purpose of this utility is to keep configuration files and directories
    under source control in a single directory, then symlink them into place.
    This program will by default look in the current working directory for a
    directory named 'dotfiles', and will create symlinks to all of them in the
    parent of the current directory with a '.' prepended.

    \b
    $HOME/
      .settings/
        dotfiles/
          bashrc
          bash_profile
          zshrc
          ssh/
            config

    if you cd into '~/.settings' and run dotinstall it will create the following symlinks:

    \b
    $HOME/
      .bashrc -> .settings/dotfiles/bashrc
      .bash_profile -> .settings/dotfiles/bash_profile
      .zshrc -> .settings/dotfiles/zshrc
      .ssh -> .settings/dotfiles/ssh

    Additionally, it can install links under a 'bin' directory, where the '.' prefix
    is not applied. This is useful when you have a number of shell scripts and want
    to link them from your version controllled directory into a location in your PATH.

    \b
    $HOME/
      .settings/
        bin/
          foo
          bar
          baz

    can be linked to

    \b
    $HOME/
      .local/
        bin/
          foo -> ../../.settings/bin/foo
          bar -> ../../.settings/bin/bar
          baz -> ../../.settings/bin/baz

    In the case of conflicts (i.e. destination already exists) you can decide
    how files and symlinks will be handled.

    If a link path already exists and is a file, the following strategies are available:

    * 'backup': move the file to a unique dated backup location and create the symlink

    * 'replace': just delete the file and create the symlink

    * 'warn': print a warning that the conflict exists and continue.

    * 'fail': stop processing and report an error.

    If a symlink exists:

    * 'replace': assume we own the symlink and recreate it pointing to the target

    * 'warn': print a warning that the conflict exists and continue

    * 'fail': stop processing and report an error
  """

  settings = _config_file_mod.load(config_file, profile)

  if dump_settings is not None:
    dump_settings.write(SettingsFactory.dumps(settings))
    return

  run(settings)


def run(settings: Settings) -> None:
  fs.apply_settings(settings)


if __name__ == '__main__':
  load_dotenv(find_dotenv())
  main(auto_envvar_prefix="DFI")
