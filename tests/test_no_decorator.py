from itertools import tee
from operator import add
from unittest import TestCase
from unittest import main as unittest_main

from cltoolbox import Program


def rest_add(a, b):
    """
    The sum of two numbers.

    :param a: The first number
    :type a: int, float

    :param b: The second number
    :type b: int, float

    :returns: the summation of the two inputs
    :rtype: int, float
    """
    return add(a, b)


def numpy_add(a, b):
    """The sum of two numbers.

    Parameters
    ----------
    a : int, float
        The first number.
    b : int, float
        The second number.

    Returns
    -------
    int, float
        The summation of the two inputs.
    """
    return add(a, b)


def google_add(a, b):
    """The sum of two numbers.

    Args:
        a (int, float): The first number.
        b (int, float): The second number.

    Returns:
        int, float: The summation of the two inputs.
    """
    return add(a, b)


# A simple helper from https://docs.python.org/3/library/itertools.html
def pairwise(iterable):
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


class NoDecoratorTest(TestCase):
    def setUp(self) -> None:
        self.program = Program("example.py", "1.0.10")

    def tearDown(self) -> None:
        del self.program

    def test_rest_no_decorator(self):
        self.program.command(rest_add)
        self.assertIn("rest_add", self.program._signatures)

    def test_numpy_no_decorator(self):
        self.program.command(numpy_add)
        self.assertIn("numpy_add", self.program._signatures)

    def test_google_no_decorator(self):
        self.program.command(google_add)
        self.assertIn("google_add", self.program._signatures)

    def test_all(self):
        all_funcs = [rest_add, numpy_add, google_add]
        signatures = []
        choices = []
        for f in all_funcs:
            self.program.command()(f)
            signatures.append(self.program._signatures[f.__name__])
            choices.append(self.program._subparsers.choices[f.__name__])

        for f in all_funcs:
            self.assertIn(f.__name__, self.program._signatures)
        for s0, s1 in pairwise(signatures):
            self.assertEqual(tuple(s0._parameters), tuple(s1._parameters))
        for c0, c1 in pairwise(choices):
            self.assertEqual(c0.description, c1.description)


if __name__ == "__main__":
    unittest_main()
