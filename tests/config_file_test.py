from pathlib import Path
from dfi import config_file
from dfi.config import Settings, OnConflict, FileGroup

from .conftest import FixturePaths

EXAMPLE_TOML_PATH = Path(__file__).resolve().parent.joinpath('example.toml')

def test_load_example(monkeypatch, example_toml_expected: Settings, df_paths: FixturePaths):
  stgs: Settings = config_file.load(EXAMPLE_TOML_PATH, "standard")
  expect = example_toml_expected
  assert stgs.base_dir == expect.base_dir
  assert stgs.on_conflict == expect.on_conflict

  assert len(stgs.file_groups) == 2
  assert stgs.file_groups[0] == expect.file_groups[0]
  assert stgs.file_groups[1] == expect.file_groups[1]
