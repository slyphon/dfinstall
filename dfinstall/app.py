
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

Configuration is possible through a dfinstall.toml file placed in the '.settings' dir
(whatever its named) which can provide the user with the ability to specify the dotfile
directories, includes, excludes, platform specific directories (i.e. 'linux-dotfiles'),
etc.

"""

def main():
  pass

