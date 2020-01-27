import os
import os.path
from pathlib import Path
from pprint import pprint
from typing import List, Iterable, Callable

import attr
import click
from dotenv import load_dotenv, find_dotenv

VALID_FILE_STRATEGIES = ['backup', 'delete', 'warn', 'fail']
VALID_SYMLINK_STRATEGIES = ['replace', 'warn', 'fail']


@attr.s(slots=True, frozen=True, auto_attribs=True)
class Config:
  """takes settings and creates a more high-level configuration object out of them"""
  conflicting_file_strategy: str
  conflicting_symlink_strategy: str
  dest_dir: Path

  dotfiles_includes: List[str]
  dotfiles_excludes: List[str]
  binfiles_includes: List[str]
  binfiles_excludes: List[str]

  @classmethod
  def from_settings(cls, s):
    pass


@click.command()
@click.option(
  '-b',
  '--base-path',
  type=click.Path(exists=True, dir_okay=True, file_okay=False, resolve_path=True, allow_dash=False),
  help="the directory above which the dotfile symlinks (by default) will be created",
  default=os.getcwd()
)
@click.option(
  '-F',
  '--file-conflict-strategy',
  'file_strategy',
  type=click.Choice(VALID_FILE_STRATEGIES, case_sensitive=False),
  help="a strategy to resolve conflicts when a dest exists and is a file"
)
@click.option(
  '-S',
  '--symlink-conflict-strategy',
  'symlink_strategy',
  type=click.Choice(VALID_SYMLINK_STRATEGIES, case_sensitive=False),
  help="a strategy to resolve conflicts when a dest exists and is a symlink"
)
@click.option(
  '--dotfile-dir', 'dotfile_dirs',
  type=click.Path(exists=True, dir_okay=True, file_okay=False, resolve_path=True, allow_dash=False),
  help='create dot-prefixed symlinks for all dirents in the given directory',
  multiple=True,
)
@click.option(
  '--dotfiles', type=click.STRING, help='a path-separated list of entries to create symlinks for'
)
@click.option(
  '--dotfile-excludes',
  type=click.STRING,
  help='a fnmatch glob that excludes certain entries from --dotfile-dir paths'
)
@click.option(
  '--dotfile-target-dir',
  type=click.Path(exists=True, dir_okay=True, file_okay=False, resolve_path=True, allow_dash=False),
  help='the directory in which we will create the dotfiles',
  default=os.path.dirname(os.getcwd())
)
@click.option(
  '--binfile-dir', 'binfile_dirs',
  type=click.Path(exists=True, dir_okay=True, file_okay=False, resolve_path=True, allow_dash=False),
  help='create non-dot-prefixed from dirents in this directory',
  multiple=True,
)
@click.option(
  '--binfiles',
  type=click.STRING,
  help='a path-separated (:) list of entries to create symlinks for',
)
@click.option(
  '--binfile-excludes',
  type=click.STRING,
  help='a fnmatch glob that excludes certain entries from --dotfile-dir paths',
)
@click.option(
  '--binfile-target-dir',
  type=click.Path(exists=True, dir_okay=True, file_okay=False, resolve_path=True, allow_dash=False),
  help='the directory in which we will create the bin links',
  default=str(Path.cwd().parent.joinpath(".local", "bin")),
)
def main(
  base_path,
  file_strategy,
  symlink_strategy,
  dotfile_dirs,
  dotfiles,
  dotfile_excludes,
  dotfile_target_dir,
  binfile_dirs,
  binfiles,
  binfile_excludes,
  binfile_target_dir,
):
  """\
The purpose of this app is to keep configuration files and directories
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


if __name__ == '__main__':
  load_dotenv(find_dotenv())
  main(auto_envvar_prefix="DFINSTALL")
