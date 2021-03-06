from ._compat import PY2 as PY2, iteritems as iteritems
from typing import Any, Optional

clickpkg: Any

class EchoingStdin:
    def __init__(self, input: Any, output: Any) -> None: ...
    def __getattr__(self, x: Any): ...
    def read(self, n: int = ...): ...
    def readline(self, n: int = ...): ...
    def readlines(self): ...
    def __iter__(self) -> Any: ...

def make_input_stream(input: Any, charset: Any): ...

class Result:
    runner: Any = ...
    output_bytes: Any = ...
    exit_code: Any = ...
    exception: Any = ...
    exc_info: Any = ...
    def __init__(self, runner: Any, output_bytes: Any, exit_code: Any, exception: Any, exc_info: Optional[Any] = ...) -> None: ...
    @property
    def output(self): ...

class CliRunner:
    charset: Any = ...
    env: Any = ...
    echo_stdin: Any = ...
    def __init__(self, charset: Optional[Any] = ..., env: Optional[Any] = ..., echo_stdin: bool = ...) -> None: ...
    def get_default_prog_name(self, cli: Any): ...
    def make_env(self, overrides: Optional[Any] = ...): ...
    def isolation(self, input: Optional[Any] = ..., env: Optional[Any] = ..., color: bool = ...): ...
    def invoke(self, cli: Any, args: Optional[Any] = ..., input: Optional[Any] = ..., env: Optional[Any] = ..., catch_exceptions: bool = ..., color: bool = ..., **extra: Any): ...
    def isolated_filesystem(self) -> None: ...
