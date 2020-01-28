from ._compat import iteritems as iteritems
from .core import Argument as Argument, Command as Command, Group as Group, Option as Option
from .globals import get_current_context as get_current_context
from .utils import echo as echo
from typing import Any, Optional

def pass_context(f: Any): ...
def pass_obj(f: Any): ...
def make_pass_decorator(object_type: Any, ensure: bool = ...): ...
def command(name: Optional[Any] = ..., cls: Optional[Any] = ..., **attrs: Any): ...
def group(name: Optional[Any] = ..., **attrs: Any): ...
def argument(*param_decls: Any, **attrs: Any): ...
def option(*param_decls: Any, **attrs: Any): ...
def confirmation_option(*param_decls: Any, **attrs: Any): ...
def password_option(*param_decls: Any, **attrs: Any): ...
def version_option(version: Optional[Any] = ..., *param_decls: Any, **attrs: Any): ...
def help_option(*param_decls: Any, **attrs: Any): ...