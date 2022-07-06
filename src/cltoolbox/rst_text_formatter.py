# -*- coding: utf-8 -*-
import argparse
import sys

from rst2ansi import rst2ansi  # type: ignore


def b(s):
    return s.encode("utf-8")


class RSTHelpFormatter(argparse.RawTextHelpFormatter):
    """
    Custom formatter class that is capable of interpreting ReST.
    """

    def format_help(self):
        ret = rst2ansi(b(super(RSTHelpFormatter, self).format_help()) + b("\n"))
        return ret.encode(sys.stdout.encoding, "replace").decode(sys.stdout.encoding)

    def format_usage(self):
        ret = rst2ansi(b(super(RSTHelpFormatter, self).format_usage()) + b("\n"))
        return ret.encode(sys.stdout.encoding, "replace").decode(sys.stdout.encoding)
