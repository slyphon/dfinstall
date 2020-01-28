from typing import Any, List
from click.types import ParamType
from os import pathsep

class SeparatedString(ParamType):
  name = 'sepstr'
  envvar_list_splitter = pathsep

  def convert(self, value: str, param: ParamType, ctx: Any) -> List[str]:
    v: str = super().convert(value, param, ctx)
    return v.split(self.envvar_list_splitter)

  def __repr__(self) -> str:
    return "SEPSTRING"


PATHSEP_STRING = SeparatedString()
