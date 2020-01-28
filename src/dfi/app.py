import os
import os.path # type: ignore # noqa
from pathlib import Path
from pprint import pprint
from typing import List, Optional, TextIO
import json

import attr
import cattr
import click
from dotenv import find_dotenv, load_dotenv

from .click_ext import PATHSEP_STRING

from .config import (
  FileGroup,
  Settings,
  VALID_FILE_STRATEGIES,
  VALID_SYMLINK_STRATEGIES,
  TFileStrategies,
  TSymlinkStrategies
)

def run(settings: Settings) -> None:
  pass


# mypy: disallow-untyped-decorators=False

@click.command()
@click.option(
  '-b',
  '--base-path',
  type=click.Path(exists=True, dir_okay=True, file_okay=False, resolve_path=True, allow_dash=False),
  help="the directory above which the dotfile symlinks (by default) will be created",
  default=lambda: os.getcwd()
)
@click.option(
  '-F',
  '--file-conflict-strategy',
  'file_strategy',
  type=click.Choice(VALID_FILE_STRATEGIES),
  help="a strategy to resolve conflicts when a dest exists and is a file", # type: ignore # wtf?
  default='backup',
)
@click.option(
  '-S',
  '--symlink-conflict-strategy',
  'symlink_strategy',
  type=click.Choice(VALID_SYMLINK_STRATEGIES),
  help="a strategy to resolve conflicts when a dest exists and is a symlink",
  default='replace',
)
@click.option(
  '--dotfile-dir',
  'dotfile_dirs',
  type=click.Path(exists=True, dir_okay=True, file_okay=False, resolve_path=True, allow_dash=False),
  help='create dot-prefixed symlinks for all dirents in the given directory',
  multiple=True,
)
@click.option(
  '--dotfiles',
  type=PATHSEP_STRING,
  help='a :-separated list of globs, relative to the base_dir, to create symlinks for'
)
@click.option(
  '--dotfile-excludes',
  type=PATHSEP_STRING,
  help='a :-separated list of fnmatch globs that excludes certain entries collected paths'
)
@click.option(
  '--dotfile-target-dir',
  type=click.Path(dir_okay=True, file_okay=False, resolve_path=True, allow_dash=False),
  help='the directory in which we will create the dotfiles',
  default=lambda: os.path.dirname(os.getcwd())
)
@click.option(
  '--binfile-dir',
  'binfile_dirs',
  type=click.Path(exists=True, dir_okay=True, file_okay=False, resolve_path=True, allow_dash=False),
  help='create non-dot-prefixed from dirents in this directory',
  multiple=True,
)
@click.option(
  '--binfiles',
  type=PATHSEP_STRING,
  help='a path-separated (:) list of globs, relative to the base_dir, to create symlinks for',
)
@click.option(
  '--binfile-excludes',
  type=PATHSEP_STRING,
  help='a :-separated list of fnmatch globs that excludes certain entries the collcted paths',
)
@click.option(
  '--binfile-target-dir',
  type=click.Path(dir_okay=True, file_okay=False, resolve_path=True, allow_dash=False),
  help='the directory in which we will create the bin links',
  default=lambda: str(Path.cwd().parent.joinpath(".local", "bin")),
)
@click.option(
  '--output-flag-settings',
  help="""dumps a configuration in json that matches the flags
    given to the path provided (or stdout for -) and exits""",
  type=click.File(mode='w', encoding='utf8'),
)
def main(
  base_path: Path,
  file_strategy: TFileStrategies,
  symlink_strategy: TSymlinkStrategies,
  dotfile_dirs: List[Path],
  dotfiles: List[str],
  dotfile_excludes: List[str],
  dotfile_target_dir: Path,
  binfile_dirs: List[Path],
  binfiles: List[str],
  binfile_excludes: List[str],
  binfile_target_dir: Path,
  output_flag_settings: Optional[TextIO]
):
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

    * 'delete': just delete the file and create the symlink

    * 'warn': print a warning that the conflict exists and continue.

    * 'fail': stop processing and report an error.

    If a symlink exists:

    * 'replace': assume we own the symlink and recreate it pointing to the target

    * 'warn': print a warning that the conflict exists and continue

    * 'fail': stop processing and report an error
  """

  settings = Settings(
    base_dir=base_path,
    conflicting_file_strategy=file_strategy,
    conflicting_symlink_strategy=symlink_strategy,
    dotfiles_file_group=FileGroup(
      base_dir=base_path,
      dirs=dotfile_dirs,
      globs=dotfiles,
      excludes=dotfile_excludes,
      target_dir=dotfile_target_dir
    ),
    binfiles_file_group=FileGroup(
      base_dir=base_path,
      dirs=binfile_dirs,
      globs=binfiles,
      excludes=binfile_excludes,
      target_dir=binfile_target_dir
    )
  )
  if output_flag_settings is not None:
    output_flag_settings.write(json.dumps(cattr.unstructure(settings)))
    return

  run(settings)


if __name__ == '__main__':
  load_dotenv(find_dotenv())
  main(auto_envvar_prefix="DFI")
