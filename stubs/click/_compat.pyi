import io
from typing import Any, Optional

PY2: Any
WIN: Any
DEFAULT_COLUMNS: int

def get_filesystem_encoding(): ...
def is_ascii_encoding(encoding: Any): ...
def get_best_encoding(stream: Any): ...

class _NonClosingTextIOWrapper(io.TextIOWrapper):
    def __init__(self, stream: Any, encoding: Any, errors: Any, **extra: Any) -> None: ...
    def __del__(self) -> None: ...
    def isatty(self): ...

class _FixupStream:
    def __init__(self, stream: Any) -> None: ...
    def __getattr__(self, name: Any): ...
    def read1(self, size: Any): ...
    def readable(self): ...
    def writable(self): ...
    def seekable(self): ...
text_type = str
raw_input = input
string_types: Any
range_type = range
isidentifier: Any
iteritems: Any

def is_bytes(x: Any): ...
def get_binary_stdin(): ...
def get_binary_stdout(): ...
def get_binary_stderr(): ...
def get_text_stdin(encoding: Optional[Any] = ..., errors: Optional[Any] = ...): ...
def get_text_stdout(encoding: Optional[Any] = ..., errors: Optional[Any] = ...): ...
def get_text_stderr(encoding: Optional[Any] = ..., errors: Optional[Any] = ...): ...
def filename_to_ui(value: Any): ...
def get_streerror(e: Any, default: Optional[Any] = ...): ...
def open_stream(filename: Any, mode: str = ..., encoding: Optional[Any] = ..., errors: str = ..., atomic: bool = ...): ...

class _AtomicFile:
    closed: bool = ...
    def __init__(self, f: Any, tmp_filename: Any, real_filename: Any) -> None: ...
    @property
    def name(self): ...
    def close(self, delete: bool = ...) -> None: ...
    def __getattr__(self, name: Any): ...
    def __enter__(self): ...
    def __exit__(self, exc_type: Any, exc_value: Any, tb: Any) -> None: ...

auto_wrap_for_ansi: Any
colorama: Any
get_winterm_size: Any

def strip_ansi(value: Any): ...
def should_strip_ansi(stream: Optional[Any] = ..., color: Optional[Any] = ...): ...
def term_len(x: Any): ...
def isatty(stream: Any): ...

binary_streams: Any
text_streams: Any
