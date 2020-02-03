from pathlib import Path
from dfi import config_file

EXAMPLE_TOML_PATH = Path(__file__).resolve().parent.joinpath('example.toml')

def test_load_example():
  config_file.load(EXAMPLE_TOML_PATH)
  pass
