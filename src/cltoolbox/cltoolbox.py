"""Main module containing the class Program(), which allows the conversion from
ordinary Python functions into commands for the command line. It uses
:py:module:``argparse`` behind the scenes.
"""

from contextlib import suppress

with suppress(ImportError):
    import argcomplete
import argparse
import inspect
import re
import sys
import textwrap

from docstring_parser import parse as ds_parse

_POSITIONAL = type("_positional", (object,), {})
_DISPATCH_TO = "_dispatch_to"


def _purify_kwargs(kwargs):
    """Remove None values for type and metavar from kwargs."""
    keys_to_remove = ["type", "metavar"]
    return {
        k: v for k, v in kwargs.items() if not ((k in keys_to_remove) and (v is None))
    }


def _action_by_type(obj):
    """Determine action and type for the given object."""
    if isinstance(obj, bool):
        return {"action": "store_false" if obj else "store_true"}
    if isinstance(obj, list):
        return {"action": "append", **_get_type(obj)}
    return _get_type(obj)


def _get_type(obj):
    """Get type if object is a basic built-in type."""
    basic_types = (int, float, str, bool)
    obj_type = type(obj)
    return {"type": obj_type} if obj_type in basic_types else {}


def _ensure_dashes(opts):
    """Add appropriate number of dashes to options."""
    return [
        opt if opt.startswith("-") else ("-" * (1 + (len(opt) > 1))) + opt
        for opt in opts
    ]


def docstring(dstr):
    """Normalizes information from the docstring to be used by cltoolbox.

    Parameters
    ----------
    dstr
        The docstring to parse.

    Returns
    -------
    tup :
        A tuple of (parsed_docstring_dict, kwargs_dict) extracted from the
        docstring.

        Example entry in the parsed_docstring_dict:

        {...,
        "start_date": {"description": "[optional, defaults to first date ...",
                       "default": '2018-01-01',
                       "arg_name": "start_date",
                       "long_description": None,
                       "short_description": "[optional, defaults to first date ...",
                       ...,
                       }
        ...,}

        Example entry in returned kwargs_dict dictionary:

        {...,
        'start_date': (['start_date'],
                       {'metavar': None,
                        'type': <class 'str'>,
                        'help': "[optional, defaults to first date ...",
                        'default': '2018-01-01',
                        }
                      ),
        ...,}
    """
    doc = ds_parse(dstr)

    doc_params = {
        i.arg_name: (
            [i.arg_name],
            {
                "metavar": None,
                "type": None,
                "help": i.description,
                "default": i.default,
            },
        )
        for i in doc.params
    }

    # Handle descriptions
    doc.long_description = doc.long_description or doc.short_description
    doc.short_description = doc.short_description or ""
    doc.long_description = doc.long_description or ""

    return doc, {k.replace("-", "_").lstrip("_"): v for k, v in doc_params.items()}


class SubProgram:
    """Manages sub-programs and their commands."""

    def __init__(self, parser, signatures):
        """Initialize a SubProgram instance.

        Parameters
        ----------
        parser : argparse.ArgumentParser
            The argument parser for this sub-program.
        signatures : dict
            A dictionary to store function signatures.
        """
        self.parser = parser
        self._subparsers = self.parser.add_subparsers()
        self._signatures = signatures

    @property
    def name(self):
        """str: The name of the sub-program."""
        return self.parser.prog

    def option(self, *args, **kwargs):
        """Add a global option to the parser.

        Parameters
        ----------
        *args :
            Arguments passed to `add_argument`.
        **kwargs :
            Keyword arguments passed to `add_argument`.

        Returns
        -------
        argparse.Action
            The added argument action.

        Raises
        ------
        AssertionError
            If positional arguments are used or the option name clashes with an
            existing attribute.
        """
        if not args or not all(arg.startswith("-") for arg in args):
            raise AssertionError("Only options (starting with '-') are supported.")

        completer = kwargs.pop("completer", None)
        arg = self.parser.add_argument(*args, **kwargs)

        if completer:
            arg.completer = completer

        if hasattr(self, arg.dest):
            raise AssertionError(
                f"Option name '{arg.dest}' clashes with an existing attribute."
            )

        return arg

    def add_subprog(self, name, **kwargs):
        """Add a sub-program.

        Parameters
        ----------
        name : str
            The name of the sub-program.
        **kwargs :
            Keyword arguments passed to `add_parser`.

        Returns
        -------
        SubProgram
            The created sub-program.

        Raises
        ------
        AssertionError
            If the sub-program name clashes with an existing attribute.
        """
        help_str = kwargs.pop("help", f"{name} subcommand")
        parser = self._subparsers.add_parser(name, help=help_str, **kwargs)
        prog = SubProgram(parser, self._signatures)

        if hasattr(self, name):
            raise AssertionError(
                f"Sub-program name '{name}' clashes with an existing attribute."
            )

        setattr(self, name, prog)
        return prog

    def command(self, *args, **kwargs):
        """Decorator to convert a function into a command.

        Parameters
        ----------
        *args :
            If a single callable is provided, it's treated as the function to
            decorate. Otherwise, it's the name of the command.
        **kwargs :
            Additional keyword arguments for the parser.

        Returns
        -------
        callable
            The decorated function or a decorator function.
        """
        if len(args) == 1 and callable(args[0]):
            return self._generate_command(args[0])

        def _command(func):
            return self._generate_command(func, *args, **kwargs)

        return _command

    @staticmethod
    def arg(param, *args, **kwargs):
        """Decorator to override or add argument parameters.

        Parameters
        ----------
        param : str
            The parameter name.
        *args :
            Arguments for `add_argument`.
        **kwargs :
            Keyword arguments for `add_argument`.

        Returns
        -------
        callable
            The decorated function.
        """

        def wrapper(func):
            if not hasattr(func, "argopts"):
                func.argopts = {}
            func.argopts[param] = (args, kwargs)
            return func

        return wrapper

    def _generate_command(self, func, name=None, *args, **kwargs):
        """Generate a command from a function.

        Parameters
        ----------
        func : callable
            The function to convert into a command.
        name : str, optional
            The command name. Defaults to the function name.
        *args :
            Arguments for `add_parser`.
        **kwargs :
            Keyword arguments for `add_parser`.

        Returns
        -------
        callable
            The original function.
        """
        name = name or func.__name__
        doc = inspect.getdoc(func) or ""
        doc, doc_params = docstring(doc)

        cmd_help, cmd_desc = doc.short_description, doc.long_description
        if cmd_desc is None:
            cmd_desc = cmd_help

        subparser = self._subparsers.add_parser(
            name, help=cmd_help or None, description=cmd_desc or None, **kwargs
        )

        self._signatures[func.__name__] = inspect.signature(func)

        for rargs, rkwds in self._analyze_func(func, doc_params):
            completer = rkwds.pop("completer", None)
            arg = subparser.add_argument(*rargs, **_purify_kwargs(rkwds))
            if completer:
                arg.completer = completer

        subparser.set_defaults(**{_DISPATCH_TO: func})
        return func

    def _analyze_func(self, func, doc_params):
        """Analyze function parameters and merge with docstring and overrides.

        Parameters
        ----------
        func : callable
            The function to analyze.
        doc_params : dict
            Parameters extracted from the docstring.

        Yields
        ------
        tuple
            A tuple containing arguments and keyword arguments for `add_argument`.
        """
        sig = self._signatures.get(func.__name__) or inspect.signature(func)
        overrides = getattr(func, "argopts", {})

        for name, param in sig.parameters.items():
            if param.kind is param.VAR_POSITIONAL:
                kwargs = {"nargs": "*"}
                kwargs.update(doc_params.get(name, (None, {}))[1])
                yield ([name], kwargs)
                continue

            default = param.default
            if default is sig.empty:
                default = _POSITIONAL()

            opts, meta = doc_params.get(name, ([], {}))
            meta["type"] = (
                param.annotation if param.annotation is not sig.empty else None
            )
            override = overrides.get(name, ((), {}))

            yield merge(name, default, override, opts, meta)


class Program(SubProgram):
    """Contains all of the sub-programs.

    Simplifies command-line argument parsing and execution.
    """

    def __init__(self, prog=None, version=None, **kwargs):
        """Initialize a Program instance.

        Creates an argument parser and sets up initial values.

        Parameters
        ----------
        prog : str, optional
            The name of the program, by default None
        version : str, optional
            The program's version string, by default None
        **kwargs :
            Additional keyword arguments passed to the argument parser.
        """
        parser = argparse.ArgumentParser(prog, **kwargs)
        if version is not None:
            parser.add_argument("-v", "--version", action="version", version=version)

        super().__init__(parser, {})
        self._options = None
        self._current_command = None

    def __getattr__(self, attr):
        """Attribute lookup fallback redirecting to options instance."""
        return getattr(self._options, attr)

    def parse(self, args):
        """Parse arguments and return command and arguments.

        Parameters
        ----------
        args : list
            List of arguments to parse.

        Returns
        -------
        tuple
            Tuple containing the command and a list of its arguments.
        """
        with suppress(NameError):
            argcomplete.autocomplete(self.parser)

        self._options = self.parser.parse_args(args)
        arg_map = vars(self._options)

        if _DISPATCH_TO not in arg_map:
            self.parser.error("Too few arguments.")

        command = arg_map.pop(_DISPATCH_TO)
        sig = self._signatures[command.__name__]
        real_args = []

        for name, param in sig.parameters.items():
            if param.kind is param.VAR_POSITIONAL:
                real_args.extend(arg_map.pop(name, []))
            else:
                real_args.append(arg_map.pop(name))

        return command, real_args

    def execute(self, args):
        """Parse arguments and execute the command.

        Parameters
        ----------
        args : list
            List of arguments to parse.

        Returns
        -------
        Any
            The return value of the executed command.
        """
        command, real_args = self.parse(args)
        self._current_command = command.__name__
        return command(*real_args)

    def __call__(self):
        """Parse sys.argv and execute the command."""
        return self.execute(sys.argv[1:])


def merge(arg, default, override, args, kwargs):
    """Merge all the possible arguments into a tuple and a dictionary.

    Parameters
    ----------
    arg :
        The argument's name.
    default :
        The argument's default value or an instance of _POSITIONAL.
    override :
        A tuple containing (args, kwargs) given to @arg.
    args :
        The arguments extracted from the docstring.
    kwargs :
        The keyword arguments extracted from the docstring.

    Returns
    -------
    tup :
        A tuple of (args, kwargs) to be passed to add_argument.
    """
    if isinstance(default, _POSITIONAL):
        # positionals can't have a metavar, otherwise the help is messed up
        # if one really wants the metavar, it can be added with @arg
        opts = [arg]
        kwargs["metavar"] = None
    else:
        opts = list(_ensure_dashes(args or [arg]))
        kwargs.update({"default": default, "dest": arg, **_action_by_type(default)})

    kwargs.update(override[1])
    return override[0] or opts, kwargs


class RSTHelpFormatter(argparse.RawTextHelpFormatter):
    """DEPRECATED: Custom formatter class that is capable of interpreting ReST."""


class FlexiHelpFormatter(argparse.HelpFormatter):
    """Help message formatter which respects paragraphs and bulleted lists.

    Only the name of this class is considered a public API. All the methods
    provided by the class are considered an implementation detail.
    """

    def _split_lines(self, text, width):
        return self._para_reformat(text, width)

    def _fill_text(self, text, width, indent):
        lines = self._para_reformat(text, width)
        return "\n".join(lines)

    def _indents(self, line):
        """Return line indent level and "sub_indent" for bullet list text."""

        indent = len(re.match(r"( *)", line)[1])
        list_match = re.match(r"( *)(([*\-+>]+|\w+\)|\w+\.) +)", line)
        sub_indent = indent + len(list_match[2]) if list_match else indent
        return (indent, sub_indent)

    def _split_paragraphs(self, text):
        """Split text in to paragraphs of like-indented lines."""

        text = textwrap.dedent(text).strip()
        text = re.sub("\n\n[\n]+", "\n\n", text)

        last_sub_indent = None
        paragraphs = []
        for line in text.splitlines():
            (indent, sub_indent) = self._indents(line)
            is_text = len(line.strip()) > 0

            if is_text and indent == sub_indent == last_sub_indent:
                paragraphs[-1] += f" {line}"
            else:
                paragraphs.append(line)

            last_sub_indent = sub_indent if is_text else None
        return paragraphs

    def _para_reformat(self, text, width):
        """Reformat text, by paragraph."""

        lines = []
        for paragraph in self._split_paragraphs(text):
            (indent, sub_indent) = self._indents(paragraph)

            paragraph = self._whitespace_matcher.sub(" ", paragraph).strip()
            new_lines = textwrap.wrap(
                text=paragraph,
                width=width,
                initial_indent=" " * indent,
                subsequent_indent=" " * sub_indent,
            )

            # Blank lines get eaten by textwrap, put it back
            lines.extend(new_lines or [""])

        return lines
