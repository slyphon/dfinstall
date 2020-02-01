import typing
from marshmallow import Schema as Schema
from marshmallow.exceptions import RegistryError as RegistryError

def register(classname: str, cls: Schema) -> None: ...
def get_class(classname: str, all: bool=...) -> typing.Union[typing.List[Schema], Schema]: ...
