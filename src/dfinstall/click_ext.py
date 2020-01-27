from click.types import ParamType
from os import pathsep

class SeparatedString(ParamType):
  name = 'sepstr'
  envvar_list_splitter = pathsep

  def convert(self, value, param, ctx):
    v = super().convert(value, param, ctx)
    return v.split(self.envvar_list_splitter)

  def __repr__(self):
    return "SEPSTRING"


PATHSEP_STRING = SeparatedString()
