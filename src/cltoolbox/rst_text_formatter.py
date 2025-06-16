"""A simple class that wraps argparse help with rst2ansi."""

import argparse
import sys

from rst2ansi import rst2ansi  # type: ignore


class RSTHelpFormatter(argparse.RawTextHelpFormatter):
    """Custom formatter class that is capable of interpreting ReST."""

    def format_help(self):
        """Override the help formatter to use rst2ansi."""
        ret = rst2ansi(bytes(super().format_help() + "\n", "utf-8"))
        return (
            ret.encode(sys.stdout.encoding, "replace").decode(sys.stdout.encoding)
            + "\n"
        )
