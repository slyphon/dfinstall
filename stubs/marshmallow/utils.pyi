import datetime as dt
import typing
from marshmallow.base import FieldABC as FieldABC
from marshmallow.exceptions import FieldInstanceResolutionError as FieldInstanceResolutionError
from typing import Any

EXCLUDE: str
INCLUDE: str
RAISE: str

class _Missing:
    def __bool__(self): ...
    def __copy__(self): ...
    def __deepcopy__(self, _: Any): ...

missing: Any

def is_generator(obj: Any) -> bool: ...
def is_iterable_but_not_string(obj: Any) -> bool: ...
def is_collection(obj: Any) -> bool: ...
def is_instance_or_subclass(val: Any, class_: Any) -> bool: ...
def is_keyed_tuple(obj: Any) -> bool: ...
def pprint(obj: Any, *args: Any, **kwargs: Any) -> None: ...
def is_aware(datetime: dt.datetime) -> bool: ...
def from_rfc(datestring: str) -> dt.datetime: ...
def rfcformat(datetime: dt.datetime) -> str: ...
def get_fixed_timezone(offset: typing.Union[int, float, dt.timedelta]) -> dt.timezone: ...
def from_iso_datetime(value: Any): ...
def from_iso_time(value: Any): ...
def from_iso_date(value: Any): ...
def isoformat(datetime: dt.datetime) -> str: ...
def to_iso_date(date: dt.date) -> str: ...
def ensure_text_type(val: typing.Union[str, bytes]) -> str: ...
def pluck(dictlist: typing.List[typing.Dict[str, typing.Any]], key: str) -> Any: ...
def get_value(obj: Any, key: typing.Union[int, str], default: Any=...) -> Any: ...
def set_value(dct: typing.Dict[str, typing.Any], key: str, value: typing.Any) -> Any: ...
def callable_or_raise(obj: Any): ...
def get_func_args(func: typing.Callable) -> typing.List[str]: ...
def resolve_field_instance(cls_or_instance: Any): ...