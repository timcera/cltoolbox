import sys

import pytest

from cltoolbox import Program

from . import capture

program = Program("example.py", "1.0.10")


@program.command()
def simple_numpy_docstring(arg1, arg2="string"):
    """One line summary.

    Extended description.

    Parameters
    ----------
    arg1 : int
        Description of `arg1`
    arg2 : str
        Description of `arg2`
    """
    return int(arg1) * arg2


GENERIC_COMMAND_CASES = [
    ("simple_numpy_docstring 2 --arg2=test", "testtest"),
]


@pytest.mark.parametrize("args,result", GENERIC_COMMAND_CASES)
def test_generic_command(args, result):
    args = args.split()
    assert result == program.execute(args)
    assert program.parse(args)[0].__name__ == program._current_command


option_title = "optional arguments"
if sys.version_info[:2] >= (3, 10):
    option_title = "options"

NUMPY_DOCSTRING_HELP_CASES = [
    (
        "simple_numpy_docstring --help 2 --arg2=test",
        f"""usage: example.py simple_numpy_docstring [-h] [--arg2 ARG2] arg1

Extended description.

positional arguments:
  arg1         Description of `arg1`

{option_title}:
  -h, --help   show this help message and exit
  --arg2 ARG2  Description of `arg2`
""",
    ),
]


@pytest.mark.parametrize("args,result", NUMPY_DOCSTRING_HELP_CASES)
def test_numpy_docstring_help(args, result):
    args = args.split()
    with pytest.raises(SystemExit), capture.capture_sys_output() as (stdout, _):
        program.execute(args)
    assert result == stdout.getvalue()
