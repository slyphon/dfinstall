import typing
from marshmallow import base as base, class_registry as class_registry, fields as ma_fields, types as types
from marshmallow.decorators import POST_DUMP as POST_DUMP, POST_LOAD as POST_LOAD, PRE_DUMP as PRE_DUMP, PRE_LOAD as PRE_LOAD, VALIDATES as VALIDATES, VALIDATES_SCHEMA as VALIDATES_SCHEMA
from marshmallow.error_store import ErrorStore as ErrorStore
from marshmallow.exceptions import StringNotCollectionError as StringNotCollectionError, ValidationError as ValidationError
from marshmallow.orderedset import OrderedSet as OrderedSet
from marshmallow.utils import EXCLUDE as EXCLUDE, INCLUDE as INCLUDE, RAISE as RAISE, get_value as get_value, is_collection as is_collection, is_instance_or_subclass as is_instance_or_subclass, is_iterable_but_not_string as is_iterable_but_not_string, missing as missing, set_value as set_value
from typing import Any

class SchemaMeta(type):
    def __new__(mcs: Any, name: Any, bases: Any, attrs: Any): ...
    @classmethod
    def get_declared_fields(mcs: Any, klass: type, cls_fields: typing.List, inherited_fields: typing.List, dict_cls: type) -> Any: ...
    def __init__(cls, name: Any, bases: Any, attrs: Any) -> None: ...
    def resolve_hooks(cls: Any) -> typing.Dict[types.Tag, typing.List[str]]: ...

class SchemaOpts:
    fields: Any = ...
    additional: Any = ...
    exclude: Any = ...
    dateformat: Any = ...
    datetimeformat: Any = ...
    render_module: Any = ...
    ordered: Any = ...
    index_errors: Any = ...
    include: Any = ...
    load_only: Any = ...
    dump_only: Any = ...
    unknown: Any = ...
    register: Any = ...
    def __init__(self, meta: Any, ordered: bool=...) -> None: ...

class Schema(base.SchemaABC, metaclass=SchemaMeta):
    TYPE_MAPPING: typing.Dict[type, typing.Type[ma_fields.Field]] = ...
    error_messages: typing.Dict[str, str] = ...
    OPTIONS_CLASS: type = ...
    opts: SchemaOpts = ...
    class Meta: ...
    declared_fields: Any = ...
    many: Any = ...
    only: Any = ...
    exclude: Any = ...
    ordered: Any = ...
    load_only: Any = ...
    dump_only: Any = ...
    partial: Any = ...
    unknown: Any = ...
    context: Any = ...
    fields: Any = ...
    load_fields: Any = ...
    dump_fields: Any = ...
    def __init__(self, *, only: types.StrSequenceOrSet=..., exclude: types.StrSequenceOrSet=..., many: bool=..., context: typing.Dict=..., load_only: types.StrSequenceOrSet=..., dump_only: types.StrSequenceOrSet=..., partial: typing.Union[bool, types.StrSequenceOrSet]=..., unknown: str=...) -> None: ...
    @property
    def dict_class(self) -> type: ...
    @property
    def set_class(self) -> type: ...
    @classmethod
    def from_dict(cls: Any, fields: typing.Dict[str, typing.Union[ma_fields.Field, type]], *, name: str=...) -> type: ...
    def handle_error(self, error: ValidationError, data: typing.Any, many: bool, **kwargs: Any) -> Any: ...
    def get_attribute(self, obj: typing.Any, attr: str, default: typing.Any) -> Any: ...
    def dump(self, obj: typing.Any, *, many: bool=...) -> Any: ...
    def dumps(self, obj: typing.Any, *args: Any, many: bool=..., **kwargs: Any) -> Any: ...
    def load(self, data: typing.Mapping, *, many: bool=..., partial: typing.Union[bool, types.StrSequenceOrSet]=..., unknown: str=...) -> Any: ...
    def loads(self, json_data: str, *, many: bool=..., partial: typing.Union[bool, types.StrSequenceOrSet]=..., unknown: str=..., **kwargs: Any) -> Any: ...
    def validate(self, data: typing.Mapping, *, many: bool=..., partial: typing.Union[bool, types.StrSequenceOrSet]=...) -> typing.Dict[str, typing.List[str]]: ...
    def on_bind_field(self, field_name: str, field_obj: ma_fields.Field) -> None: ...
BaseSchema = Schema
