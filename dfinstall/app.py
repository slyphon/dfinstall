from pathlib import Path
from pprint import pprint
from typing import List

import attr
import click

HELP = """\
The purpose of this app is to keep configuration files and directories
under source control in a single directory, then symlink them into place.
This program will by default look in the current working directory for a
directory named 'dotfiles', and will create symlinks to all of them in the
parent of the current directory with a '.' prepended.

$HOME/
  .settings/
    dotfiles/
      bashrc
      bash_profile
      zshrc
      ssh/
        config

if you cd into '~/.settings' and run dotinstall it will create the following symlinks:

$HOME/
  .bashrc -> .settings/dotfiles/bashrc
  .bash_profile -> .settings/dotfiles/bash_profile
  .zshrc -> .settings/dotfiles/zshrc
  .ssh -> .settings/dotfiles/ssh

Additionally, it can install links under a 'bin' directory, where the '.' prefix
is not applied. This is useful when you have a number of shell scripts and want
to link them from your version controllled directory into a location in your PATH.

$HOME/
  .settings/
    bin/
      foo
      bar
      baz

can be linked to

$HOME/
  .local/
    bin/
      foo -> ../../.settings/bin/foo
      bar -> ../../.settings/bin/bar
      baz -> ../../.settings/bin/baz


"""


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


@click.argument('--base-path')
@click.command()
def main():
  from .conf import mk_settings

  s = mk_settings()
  pprint(s.as_dict())


if __name__ == '__main__':
  main()
