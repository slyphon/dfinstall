from ._compat import PY2 as PY2, WIN as WIN, get_best_encoding as get_best_encoding, isatty as isatty, open_stream as open_stream, range_type as range_type, strip_ansi as strip_ansi, term_len as term_len
from .exceptions import ClickException as ClickException
from .utils import echo as echo
from typing import Any, Optional

BEFORE_BAR: str
AFTER_BAR: str

class ProgressBar:
    fill_char: Any = ...
    empty_char: Any = ...
    bar_template: Any = ...
    info_sep: Any = ...
    show_eta: Any = ...
    show_percent: Any = ...
    show_pos: Any = ...
    item_show_func: Any = ...
    label: Any = ...
    file: Any = ...
    color: Any = ...
    width: Any = ...
    autowidth: Any = ...
    iter: Any = ...
    length: Any = ...
    length_known: Any = ...
    pos: int = ...
    avg: Any = ...
    start: Any = ...
    eta_known: bool = ...
    finished: bool = ...
    max_width: Any = ...
    entered: bool = ...
    current_item: Any = ...
    is_hidden: Any = ...
    def __init__(self, iterable: Any, length: Optional[Any] = ..., fill_char: str = ..., empty_char: str = ..., bar_template: str = ..., info_sep: str = ..., show_eta: bool = ..., show_percent: Optional[Any] = ..., show_pos: bool = ..., item_show_func: Optional[Any] = ..., label: Optional[Any] = ..., file: Optional[Any] = ..., color: Optional[Any] = ..., width: int = ...) -> None: ...
    def __enter__(self): ...
    def __exit__(self, exc_type: Any, exc_value: Any, tb: Any) -> None: ...
    def __iter__(self) -> Any: ...
    def render_finish(self) -> None: ...
    @property
    def pct(self): ...
    @property
    def time_per_iteration(self): ...
    @property
    def eta(self): ...
    def format_eta(self): ...
    def format_pos(self): ...
    def format_pct(self): ...
    def format_progress_line(self): ...
    def render_progress(self) -> None: ...
    last_eta: Any = ...
    def make_step(self, n_steps: Any) -> None: ...
    def update(self, n_steps: Any) -> None: ...
    def finish(self) -> None: ...
    def next(self): ...
    __next__: Any = ...

def pager(text: Any, color: Optional[Any] = ...): ...

class Editor:
    editor: Any = ...
    env: Any = ...
    require_save: Any = ...
    extension: Any = ...
    def __init__(self, editor: Optional[Any] = ..., env: Optional[Any] = ..., require_save: bool = ..., extension: str = ...) -> None: ...
    def get_editor(self): ...
    def edit_file(self, filename: Any) -> None: ...
    def edit(self, text: Any): ...

def open_url(url: Any, wait: bool = ..., locate: bool = ...): ...
def getchar(echo: Any): ...
