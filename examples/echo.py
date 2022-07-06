# -*- coding: utf-8 -*-
from cltoolbox import command, main


@command
def echo(text, capitalize=False):
    """Echo the given text."""
    if capitalize:
        text = text.upper()
    print(text)


if __name__ == "__main__":
    main()
