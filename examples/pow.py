from cltoolbox import command, main


@command
def pow(base, exp):
    """Compute base ^ exp.

    :param int base : The base.
    :param int exp : The exponent.
    """
    print(base**exp)


if __name__ == "__main__":
    main()
