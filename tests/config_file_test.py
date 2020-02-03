from pathlib import Path
from dfi import config_file
from dfi.config import Settings, OnConflict, FileGroup

EXAMPLE_TOML_PATH = Path(__file__).resolve().parent.joinpath('example.toml')

def test_load_example(monkeypatch):
  monkeypatch.setenv('HOME', '/home/foo')
  home_path = Path('/home/foo')
  base_path = home_path.joinpath('.settings')

  stgs: Settings = config_file.load(EXAMPLE_TOML_PATH, "standard")
  expect = Settings(
    base_dir=base_path,
    on_conflict=OnConflict(file='backup', symlink='replace'),
    file_groups=[
      FileGroup(
        base_dir=base_path,
        target_dir=home_path,
        dirs=[Path("dotfiles")],
        globs=['dotfile_linux/*'],
        excludes=['gnome'],
        link_prefix='.',
        on_conflict=OnConflict(file='backup', symlink='replace'),
      ),
      FileGroup(
        base_dir=base_path,
        target_dir=home_path / '.local' / 'bin',
        dirs=[Path('bin')],
        globs=['bin_darwin/pbcopy', 'bin_darwin/launched'],
        excludes=[],
        link_prefix='',
        on_conflict=OnConflict(file='backup', symlink='replace'),
      )
    ]
  )
  assert stgs.base_dir == expect.base_dir
  assert stgs.on_conflict == expect.on_conflict

  assert len(stgs.file_groups) == 2
  assert stgs.file_groups[0] == expect.file_groups[0]
  assert stgs.file_groups[1] == expect.file_groups[1]
