Usage
=====

Defining commands
-----------------
A command is a function decorated with ``@command``. cltoolbox extracts
as much as information as possible from the function's docstring and
function signature.

The argparse library is configured by cltoolbox from three different sources.

    1. Function signature
        - each argument **name**
        - each argument **type** (from type hints)
    2. Function docstring (Sphinx, Google, Numpy, or epydoc formats)
        - function **help** which is the first paragraph of the docstring and
          shouldn't be longer than one line.
        - function **description** is taken from the remaining paragraphs up
          until the documentation of arguments.
        - each argument help
    3. The ``cltoolbox.arg`` decorator which overrides or appends to any of
       the information found in the function signature or docstring.

Note that the argument types in the function docstring are ignored and do not
override the type hints found in the function signature.

For example, this program uses Sphinx formatted docstring::

    from cltoolbox import command, main

    @command
    def cmd(foo, bar):
        """Here stands the help.

        And here the description of this useless command.

        :param foo: Well, the first arg.
        :param bar: Obviously the second arg. Nonsense."""

        print(foo, bar)

    if __name__ == "__main__":
        main()

The cltoolbox will take the previous function and docstring to create the
following documentation available at the command line.

.. code-block:: console

    $ python command.py -h
    usage: command.py [-h] {cmd} ...

    positional arguments:
      {cmd}
        cmd       Here stands the help.

    optional arguments:
      -h, --help  show this help message and exit

.. code-block:: console

    $ python command.py cmd -h
    usage: command.py cmd [-h] foo bar

    And here the description of this useless command.

    positional arguments:
      foo         Well, the first arg.
      bar         Obviously the second arg. Nonsense.

    optional arguments:
      -h, --help  show this help message and exit

Overriding arguments with ``@arg``
----------------------------------
You may need to specify some argument to argparse, and it is not possible to
include in the docstring or function signature.  cltoolbox provides the
``@arg`` decorator to accomplish this. Its signature is as follows:
``@arg(arg_name, *args, **kwargs)``, where ``arg_name`` must be among the
function's arguments, while the remaining arguments will be directly passed to
``argparse.add_argument()``.

Note that this decorator will override other arguments that cltoolbox inferred
either from the function signature or from the docstring.

The following are the ``argparse.add_argument()`` positional and keyword
arguments:

Positional (if used must be first in ``@arg``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
name or flags
    Either a name or a list of option strings, e.g. foo or -f, --foo.

Keyword arguments
~~~~~~~~~~~~~~~~~
action
    The basic type of action to be taken when this argument is encountered at
    the command line.
nargs
    The number of command-line arguments that should be consumed.
const
    A constant value required by some action and nargs selections.
default
    The value produced if the argument is absent from the command line and if
    it is absent from the namespace object.
type
    The type to which the command-line argument should be converted.
choices
    A container of the allowable values for the argument.
required
    Whether or not the command-line option may be omitted (optionals only).
help
    A brief description of what the argument does.
metavar
    A name for the argument in usage messages.
dest
    The name of the attribute to be added to the object returned by
    parse_args().

Long and short options (flags)
------------------------------
The ``@arg`` decorator is useful for allowing long and short options for the
keyword arguments.

Example::

    from cltoolbox import command, main, arg

    @command
    @arg("spam", "--spam", "-s")
    def ex(foo, b=None, spam=None):
        """Nothing interesting.

        :param foo: Bla bla.
        :param b: A little flag.
        :param spam: Spam spam spam spam."""

        print((foo, b, spam))

    if __name__ == "__main__":
        main()

Usage:

.. code-block:: console

    $ python short_options.py ex -h
    usage: short_options.py ex [-h] [-b B] [--spam SPAM] foo

    positional arguments:
      foo                   Bla bla.

    optional arguments:
      -h, --help            show this help message and exit
      -b B                  A little flag.
      --spam SPAM, -s SPAM  Spam spam spam spam.

.. code-block:: console

    $ python short_options.py ex 2
    ('2', None, None)

.. code-block:: console

    $ python short_options.py ex 2 -b 8
    ('2', '8', None)

.. code-block:: console

    $ python short_options.py ex 2 -b 8 -s 9
    ('2', '8', '9')

.. code-block:: console

    $ python short_options.py ex 2 -b 8 --spam 9
    ('2', '8', '9')


How default arguments are handled
---------------------------------
If an argument has a default, then cltoolbox takes it as an optional argument,
while those which do not have a default are interpreted as positional
arguments. Here are the actions taken by cltoolbox when a default argument is
encountered:

+------------------------+-----------------------------------------------------+
| Default argument type  |   What cltoolbox specifies in ``add_argument()``    |
+========================+=====================================================+
| bool                   | *action* ``store_true`` or ``store_false`` is added |
+------------------------+-----------------------------------------------------+
| list                   | *action* ``append`` is added.                       |
+------------------------+-----------------------------------------------------+
| int                    | *type* ``int()`` is added.                          |
+------------------------+-----------------------------------------------------+
| float                  | *type* ``float()`` is added.                        |
+------------------------+-----------------------------------------------------+
| str                    | *type* ``str()`` is added.                          |
+------------------------+-----------------------------------------------------+

So, for example, if a default argument is an integer, cltoolbox will automatically
convert command line arguments to ``int()``::

    from cltoolbox import command, main

    @command
    def po(a=2, b=3):
        print(a ** b)

    if __name__ == "__main__":
        main()

.. code-block:: console

    $ python default_args.py po -h
    usage: default_args.py po [-h] [-a A] [-b B]

    optional arguments:
      -h, --help  show this help message and exit
      -a A
      -b B

.. code-block:: console

    $ python default_args.py po -a 4 -b 9
    262144

Note that passing the arguments positionally does not work, because
``argparse`` expects optional args and ``a`` and ``b`` are already filled with
defaults:

.. code-block:: console

    $ python default_args.py po
    8

.. code-block:: console

    $ python default_args.py po 9 8
    usage: default_args.py [-h] {po} ...
    default_args.py: error: unrecognized arguments: 9 8

To overcome this, cltoolbox allows you to specify positional arguments' types in
the type hints, as explained in the next section.

Adding *type*
-------------
This is especially useful for positional arguments, but it can be used for
all type of arguments.

Adding *type* in the signature
------------------------------
The cltoolbox can use type annotations to convert argument types.

Simple usage::

    from cltoolbox import command, main, arg

    @command
    @arg("mod", "--mod", "-m")
    def pow(a:float, b:float, mod:int=None):
        """Mimic Python's pow() function.

        :param a: The base.
        :param b: The exponent.
        :param mod: Modulus."""

        if mod is not None:
            print((a ** b) % mod)
        else:
            print(a ** b)

    if __name__ == "__main__":
        main()

.. code-block:: console

    $ python types.py pow -h
    usage: types.py pow [-h] [-m <int>] a b

    Mimic Python's pow() function.

    positional arguments:
      a                     The base.
      b                     The exponent.

    optional arguments:
      -h, --help            show this help message and exit
      -m <int>, --mod <int>
                            Modulus.

.. code-block:: console

    $ python types.py pow 5 8
    390625.0

.. code-block:: console

    $ python types.py pow 4.5 8.3
    264036.437449

Since type annotations can be any callable, this allows more flexibility
to convert what is given on the command line.

.. code-block:: console

    $ python types.py pow 5 8 -m 8
    1.0

.. code-block:: python

    from cltoolbox import command, main


    # Note: don't actually do this.
    def double_int(n):
        return int(n) * 2


    @command
    def dup(string, times: double_int):
        """
        Duplicate text.

        :param string: The text to duplicate.
        :param times: How many times to duplicate.
        """
        print(string * times)


    if __name__ == "__main__":
        main()

.. code-block:: console

    $ python3 dup_type_hints.py dup "test " 2
    test test test test

.. code-block:: console

    $ python3 dup_type_hints.py dup "test " foo
    usage: dup_type_hints.py dup [-h] string times
    dup_type_hints.py dup: error: argument times: invalid double_int value: 'foo'

``@command`` Arguments
----------------------
There are two special arguments to the ``@command()`` decorator to allow for
special processing for the decorated function. The first argument, also
available as keyword ``name='alias_name'`` will allow for an alias of the
command.  The second is only available as keyword
``formatter_class='argparse_formatter_class'`` to format the display of the
docstring.

Aliasing Commands
~~~~~~~~~~~~~~~~~
A common use-case for this is represented by a function with underscores in it.
Usually commands have dashes instead. So, you may specify the aliasing name to
the ``@command()`` decorator, this way::

    @command('very-powerful-cmd')
    def very_powerful_cmd(arg, verbose=False):
        pass

And call it as follows:

.. code-block:: console

    $ python prog.py very-powerful-cmd 2 --verbose

Note that the original name will be discarded and won't be usable.

.. _docstring-style:

Docstring Formats
~~~~~~~~~~~~~~~~~
There are three commonly accepted formats for docstrings. The Sphinx or
Restructured Text (REST) is the Python default, and the other two common styles are
``numpy`` and ``google``. cltoolbox will auto-detect the style used.

An example of using a Numpy formatted docstring in cltoolbox::

    @command
    def simple_numpy_docstring(arg1, arg2="string"):
        '''One line summary.

        Extended description.

        Parameters
        ----------
        arg1 : int
            Description of `arg1`
        arg2 : str
            Description of `arg2`

        Returns
        -------
        str
            Description of return value.
        '''
        return int(arg1) * arg2

An example of using a Google formatted docstring in cltoolbox::

    @command
    def simple_google_docstring(arg1, arg2="string"):
        '''One line summary.

        Extended description.

        Args:
          arg1(int): Description of `arg1`
          arg2(str): Description of `arg2`
        Returns:
          str: Description of return value.
        '''
        return int(arg1) * arg2

Formatter Class
~~~~~~~~~~~~~~~
For the help display there is the opportunity to use special formatters. Any
argparse compatible formatter class can be used. There is an alternative
formatter class available with cltoolbox that will display on ANSI terminals.

The ANSI formatter class has to be imported from cltoolbox and used as follows::

    from cltoolbox.rst_text_formatter import RSTHelpFormatter

    @command(formatter_class=RSTHelpFormatter)
    def pow(a:float, b:float, mod:int=None):
        '''Mimic Python's pow() function.

        :param a: The base.
        :param b: The exponent.
        :param mod: Modulus.'''

        if mod is not None:
            print((a ** b) % mod)
        else:
            print(a ** b)

Shell autocompletion
--------------------
The cltoolbox supports autocompletion via the optional dependency
``argcomplete``. If that package is installed, cltoolbox detects it
automatically without the need to
do anything else.
