import json
import os
import logging

import cattr
import pytest
from click.testing import Result, CliRunner

from dfi import app
from dfi.config import Settings, FileGroup, OnConflict

from .conftest import chdir

log = logging.getLogger(__name__)

def dump_click_result(res: Result) -> None:
  if res.stderr_bytes:
    log.error(f"stderr: \n{res.stderr}")
  if res.stdout_bytes:
    log.error(f"stdout: \n{res.stdout}")

@pytest.mark.xfail(strict=False)
def test_app_flag_parsing_dotfiles(df_paths, cli_runner: CliRunner):
  dotfiles_arg = ':'.join([
    str(df.relative_to(df_paths.base_dir)) for df in df_paths.dotfile_extras
  ])

  # yapf: disable
  with chdir(df_paths.base_dir):
    result: Result = cli_runner.invoke(
      app.main,
      args=[
        '--file-conflict-strategy=replace',
        '--symlink-conflict-strategy=fail',
        f'--dotfile-dir={df_paths.dotfiles_dir}',
        f'--dotfiles={dotfiles_arg}',
        '--dotfile-excludes', '.*:tux',
        '--output-flag-settings', '-',
      ],
      mix_stderr=False,
    )
    # yapf: enable

    dump_click_result(result)
    if result.exit_code != 0:
      if result.exception is not None:
        raise result.exception from None

    assert result.exit_code == 0
    assert len(result.output) > 0

    ser_set = json.loads(result.output)

    settings: Settings = cattr.structure(ser_set, Settings)

    assert settings.base_dir == df_paths.base_dir
    assert settings.on_conflict.file == 'replace'
    assert settings.on_conflict.symlink == 'fail'

    assert len(settings.file_groups) == 2

    assert settings.file_groups[0] == FileGroup(
      base_dir=df_paths.base_dir,
      dirs=[df_paths.dotfiles_dir],
      globs=dotfiles_arg.split(":"),
      excludes=['.*', 'tux'],
      target_dir=df_paths.home_dir,
      on_conflict=OnConflict(),
    )

    assert settings.file_groups[1] == FileGroup(
      base_dir=df_paths.base_dir,
      dirs=[],
      globs=None,
      excludes=None,
      target_dir=df_paths.home_dir / '.local' / 'bin',
      on_conflict=OnConflict(),
    )
