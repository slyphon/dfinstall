from ._compat import PY2 as PY2, iteritems as iteritems
from typing import Any, Optional, ByteString, Union, Tuple, Type, Dict, IO, Iterable, List, Iterator
from typing_extensions import ContextManager
from types import TracebackType
from io import StringIO

clickpkg: Any

TInput = Union[IO, str, bytes]
TSysExcInfo = Union[Tuple[Type[BaseException], BaseException, TracebackType],
                    Tuple[None, None, None]]
TEnv = Dict[str, str]
TArgs = Union[Iterable[str], str]


class EchoingStdin:
  def __init__(self, input: TInput, output: StringIO) -> None:
    ...

  def __getattr__(self, x: Any):
    ...

  def read(self, n: int = ...) -> bytes:
    ...

  def readline(self, n: int = ...) -> bytes:
    ...

  def readlines(self) -> List[bytes]:
    ...

  def __iter__(self) -> Iterator[bytes]:
    ...


def make_input_stream(input: TInput, charset: str) -> IO:
  ...


class Result:
  runner: 'CliRunner' = ...
  output_bytes: Optional[ByteString] = ...
  exit_code: int = ...
  exception: Optional[Exception] = ...
  exc_info: TSysExcInfo = ...

  def __init__(
    self,
    runner: 'CliRunner',
    output_bytes: bytes,
    exit_code: int,
    exception: Optional[Exception],
    exc_info: Optional[TSysExcInfo] = ...
  ) -> None:
    ...

  @property
  def output(self) -> str:
    ...


class CliRunner:
  charset: str = ...
  env: Dict[str, str] = ...
  echo_stdin: bool = ...

  def __init__(
    self,
    charset: Optional[TInput] = ...,
    env: Optional[TEnv] = ...,
    echo_stdin: bool = ...,
    mix_stderr: bool = ...
  ) -> None:
    ...

  def get_default_prog_name(self, cli: 'CliRunner') -> str:
    ...

  def make_env(self, overrides: Optional[TEnv] = ...) -> TEnv:
    ...

  def isolation(self,
                input: Optional[TInput] = ...,
                env: Optional[TEnv] = ...,
                color: bool = ...) -> ContextManager[Tuple[ByteString, bool]]:
    ...

  def invoke(
    self,
    cli: 'CliRunner',
    args: Optional[TArgs] = ...,
    input: Optional[TInput] = ...,
    env: Optional[TEnv] = ...,
    catch_exceptions: bool = ...,
    color: bool = ...,
    **extra: Dict[Any, Any]
  ):
    ...

  def isolated_filesystem(self) -> ContextManager[Any]:
    ...
