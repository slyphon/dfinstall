from typing import Any, Optional, TypeVar, Callable

PRE_DUMP: str
POST_DUMP: str
PRE_LOAD: str
POST_LOAD: str
VALIDATES: str
VALIDATES_SCHEMA: str

_T = TypeVar('_T')
_HookFn = Callable[..., Any]
_F = TypeVar('_F', bound=_HookFn)

def validates(field_name: str) -> Any:
  ...


def validates_schema(
  fn: Optional[Any] = ...,
  pass_many: bool = ...,
  pass_original: bool = ...,
  skip_on_field_errors: bool = ...
):
  ...


def pre_dump(fn: _F = ..., pass_many: bool = ...) -> _F:
  ...


def post_dump(fn: _F = ..., pass_many: bool = ..., pass_original: bool = ...) -> _F:
  ...


def pre_load(fn: _F = ..., pass_many: bool = ...) -> _F:
  ...


def post_load(fn: _F = ..., pass_many: bool = ..., pass_original: bool = ...) -> _F:
  ...


def set_hook(fn: Any, key: Any, **kwargs: Any):
  ...
