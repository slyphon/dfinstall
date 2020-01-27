# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'

# %%
from typing import Callable, List
from more_itertools import collapse
from pathlib import Path
from itertools import chain, filterfalse

BASE_DIR = Path('~/.settings').expanduser()
EXCLUDES = ["*.old", "*.bak", ".*"]
BIN_EXCLUDES = ['ack', 'adium*', 'backup-*', 'boiler', 'disable-*', 'gen*', 'iat*', 'lein', 'rb*']


#binfiles = collect(BASE_DIR, dirs=[Path('bin')], excludes=list(chain(EXCLUDES, BIN_EXCLUDES)))


# %%
bin_dir = Path.home().joinpath(".local", "bin")


