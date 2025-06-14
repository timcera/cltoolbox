.. image:: https://github.com/timcera/cltoolbox/actions/workflows/pypi-package.yml/badge.svg
    :alt: Tests
    :target: https://github.com/timcera/cltoolbox/actions/workflows/pypi-package.yml
    :height: 20

.. image:: https://img.shields.io/coveralls/github/timcera/cltoolbox
    :alt: Test Coverage
    :target: https://coveralls.io/r/timcera/cltoolbox?branch=master
    :height: 20

.. image:: https://img.shields.io/pypi/v/cltoolbox.svg
    :alt: Latest release
    :target: https://pypi.python.org/pypi/cltoolbox/
    :height: 20

.. image:: http://img.shields.io/pypi/l/cltoolbox.svg
    :alt: BSD-3 clause license
    :target: https://pypi.python.org/pypi/cltoolbox/
    :height: 20

.. image:: https://img.shields.io/pypi/pyversions/cltoolbox
    :alt: PyPI - Python Version
    :target: https://pypi.org/project/cltoolbox/
    :height: 20

cltoolbox: Easy Command Line Interfaces
=======================================
cltoolbox is a wrapper around ``argparse``, and allows you to write complete CLI
applications in seconds using a simple decorator.

Significant portions of this code are based on `mando`.  The primary
differences between `mando` and `cltoolbox` are:

    * `cltoolbox` supports automatic detection of Sphinx, Google, and Numpy
      docstring formats by using the `docstring_parser` library
    * `cltoolbox` supports python 3.7+

If you need support of the `mando` formatted docstring or python 2 you have to
use `mando` instead of `cltoolbox`.

Installation
------------
pip
~~~
.. code-block:: bash

    pip install cltoolbox

conda
~~~~~
.. code-block:: bash

    conda install -c conda-forge cltoolbox

The problem
-----------
The ``argparse`` module that comes with Python requires a programmer to
duplicate information that Python can easily parse from the function signature
and docstring.  The ``cltoolbox`` does this for you by using decorators.

Quickstart
----------

.. code-block:: python

    from cltoolbox import command, main


    @command
    def echo(text, capitalize=False):
        """Echo the given text."""
        if capitalize:
            text = text.upper()
        print(text)


    if __name__ == "__main__":
        main()

Generated help:

.. code-block:: console

    $ python example.py -h
    usage: example.py [-h] {echo} ...

    positional arguments:
      {echo}
        echo      Echo the given text.

    optional arguments:
      -h, --help  show this help message and exit

    $ python example.py echo -h
    usage: example.py echo [-h] [--capitalize] text

    Echo the given text.

    positional arguments:
      text

    optional arguments:
      -h, --help    show this help message and exit
      --capitalize

Actual usage:

.. code-block:: console

    $ python example.py echo spam
    spam
    $ python example.py echo --capitalize spam
    SPAM


A *real* example
----------------

Something more complex and real-world-*ish*. The code:

.. code-block:: python

    from cltoolbox import command, main


    @command
    def push(repository, all=False, dry_run=False, force=False, thin=False):
        """Update remote refs along with associated objects.

        :param repository: Repository to push to.
        :param --all: Push all refs.
        :param -n, --dry-run: Dry run.
        :param -f, --force: Force updates.
        :param --thin: Use thin pack."""

        print(
            "Pushing to {0}. All: {1}, dry run: {2}, force: {3}, thin: {4}".format(
                repository, all, dry_run, force, thin
            )
        )


    if __name__ == "__main__":
        main()

cltoolbox understands Sphinx, Google, and Numpy dostrings, from which it can
create short options and their help for you.

.. code-block:: console

    $ python git.py push -h
    usage: git.py push [-h] [--all] [-n] [-f] [--thin] repository

    Update remote refs along with associated objects.

    positional arguments:
      repository     Repository to push to.

    optional arguments:
      -h, --help     show this help message and exit
      --all          Push all refs.
      -n, --dry-run  Dry run.
      -f, --force    Force updates.
      --thin         Use thin pack.

Let's try it!

.. code-block:: console

    $ python git.py push --all myrepo
    Pushing to myrepo. All: True, dry run: False, force: False, thin: False

    $ python git.py push --all -f myrepo
    Pushing to myrepo. All: True, dry run: False, force: True, thin: False

    $ python git.py push --all -fn myrepo
    Pushing to myrepo. All: True, dry run: True, force: True, thin: False

    $ python git.py push --thin -fn myrepo
    Pushing to myrepo. All: False, dry run: True, force: True, thin: True

    $ python git.py push --thin
    usage: git.py push [-h] [--all] [-n] [-f] [--thin] repository
    git.py push: error: too few arguments

Amazed uh? Yes, cltoolbox got the short options and the help from the docstring!
You can put much more in the docstring, and if that isn't enough, there's an
``@arg`` decorator to customize the arguments that get passed to argparse.


Type annotations
----------------

cltoolbox understands Python 3-style type annotations and will warn the user if the
arguments given to a command are of the wrong type.

.. code-block:: python

    from cltoolbox import command, main


    @command
    def duplicate(string, times: int):
        """Duplicate text.

        :param string: The text to duplicate.
        :param times: How many times to duplicate."""

        print(string * times)


    if __name__ == "__main__":
        main()

.. code-block:: console

    $ python3 test.py duplicate "test " 5
    test test test test test

    $ python3 test.py duplicate "test " foo
    usage: test.py duplicate [-h] string times
    test.py duplicate: error: argument times: invalid int value: 'foo'


The `cltoolbox` supports shell autocompletion via the
``argcomplete`` package and supports custom format classes. For a complete
documentation, visit https://timcera.bibucket.io/cltoolbox/.
