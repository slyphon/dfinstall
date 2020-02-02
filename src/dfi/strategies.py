from typing import Any, List, TypeVar, Union, cast

from typing_extensions import Final, Literal

TSymlinkStrategy = Literal['replace', 'warn', 'fail']
TFileStrategy = Union[Literal['backup'], TSymlinkStrategy]

VALID_FILE_STRATEGIES: Final[List[TFileStrategy]] = ['backup', 'replace', 'warn', 'fail']
VALID_SYMLINK_STRATEGIES: Final[List[TSymlinkStrategy]] = ['replace', 'warn', 'fail']

T = TypeVar('T')


def _literal_value_assertion(valid: List[T], obj: Any) -> T:
  if obj in valid:
    return cast(T, obj)
  else:
    raise ValueError(f"{obj!r} is not a valid value: {valid!r}")


def ensure_is_file_strategy(any: Any) -> TFileStrategy:
  return _literal_value_assertion(VALID_FILE_STRATEGIES, any)


def ensure_is_symlink_strategy(any: Any) -> TSymlinkStrategy:
  return _literal_value_assertion(VALID_SYMLINK_STRATEGIES, any)


__all__ = (
  'VALID_FILE_STRATEGIES',
  'VALID_SYMLINK_STRATEGIES',
  'ensure_is_file_strategy',
  'ensure_is_symlink_strategy'
)
