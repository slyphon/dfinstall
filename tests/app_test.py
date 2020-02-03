import json
import os
import logging
from typing import List
from functools import wraps

import cattr
import pytest
from click.testing import Result, CliRunner

from dfi import app
from dfi.config import Settings, FileGroup, OnConflict
from dfi.schema import SettingsFactory

from .conftest import chdir, FixturePaths

log = logging.getLogger(__name__)

def dump_click_result(res: Result) -> None:
  if res.stderr_bytes:
    log.error(f"stderr: \n{res.stderr}")
  if res.stdout_bytes:
    log.error(f"stdout: \n{res.stdout}")

@pytest.fixture()
def run_app_test(df_paths: FixturePaths, cli_runner: CliRunner, example_toml_expected: Settings):
  def callback(*args):
    flags = ['--dump-settings', '-', *list(args)]

    result: Result = cli_runner.invoke(
      app.main,
      args=flags,
      mix_stderr=False,
    )
    # yapf: enable

    dump_click_result(result)
    if result.exit_code != 0:
      if result.exception is not None:
        raise result.exception from None

    assert result.exit_code == 0
    assert len(result.output) > 0
    loaded = SettingsFactory.loads(result.output)
    ex = example_toml_expected

    assert loaded.base_dir == ex.base_dir
    assert loaded.on_conflict == ex.on_conflict
    assert len(loaded.file_groups) == 2
    assert loaded.file_groups[0] == ex.file_groups[0]
    assert loaded.file_groups[1] == ex.file_groups[1]
  return callback

def test_config_loading_with_explicit_flag(df_paths, run_app_test):
  run_app_test('--config-file', str(df_paths.example_toml))

def test_config_loading_with_env_var(monkeypatch, df_paths, run_app_test):
  monkeypatch.setenv("DFI_CONFIG_FILE", str(df_paths.example_toml))
  run_app_test()

def test_config_loading_from_default_config_file_in_cwd(df_paths, run_app_test):
  with chdir(df_paths.base_dir):
    run_app_test()
