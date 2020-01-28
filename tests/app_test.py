import json
import os

import cattr
import pytest
from click.testing import Result

from dfi import app
from dfi.config import Settings, FileGroup

from .conftest import chdir


def test_app_flag_parsing_dotfiles(df_paths, cli_runner):
  dotfiles_arg = ':'.join([
    str(df.relative_to(df_paths.base_dir)) for df in df_paths.dotfile_extras
  ])

  # yapf: disable
  with chdir(df_paths.base_dir):
    result: Result = cli_runner.invoke(
      app.main,
      args=[
        '--file-conflict-strategy=delete',
        '--symlink-conflict-strategy=fail',
        f'--dotfile-dir={df_paths.dotfiles_dir}',
        f'--dotfiles={dotfiles_arg}',
        '--dotfile-excludes', '.*:tux',
        '--output-flag-settings', '-',
      ]
    )
    # yapf: enable

    assert result.exit_code == 0
    assert len(result.output) > 0

    ser_set = json.loads(result.output)

    settings: Settings = cattr.structure(ser_set, Settings)

    assert settings.base_dir == df_paths.base_dir
    assert settings.conflicting_file_strategy == 'delete'
    assert settings.conflicting_symlink_strategy == 'fail'

    assert settings.dotfiles_file_group == FileGroup(
      base_dir=df_paths.base_dir,
      dirs=[df_paths.dotfiles_dir],
      globs=dotfiles_arg.split(":"),
      excludes=['.*', 'tux'],
      target_dir=df_paths.home_dir
    )

    assert settings.binfiles_file_group == FileGroup(
      base_dir=df_paths.base_dir,
      dirs=[],
      globs=None,
      excludes=None,
      target_dir=df_paths.home_dir / '.local' / 'bin'
    )
