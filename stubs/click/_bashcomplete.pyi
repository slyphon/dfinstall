from .core import MultiCommand as MultiCommand, Option as Option
from .parser import split_arg_string as split_arg_string
from .utils import echo as echo
from typing import Any

COMPLETION_SCRIPT: str

def get_completion_script(prog_name: Any, complete_var: Any): ...
def resolve_ctx(cli: Any, prog_name: Any, args: Any): ...
def get_choices(cli: Any, prog_name: Any, args: Any, incomplete: Any) -> None: ...
def do_complete(cli: Any, prog_name: Any): ...
def bashcomplete(cli: Any, prog_name: Any, complete_var: Any, complete_instr: Any): ...