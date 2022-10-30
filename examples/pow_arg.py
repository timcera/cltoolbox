from cltoolbox import arg, command, main


@command
@arg("base", type=int)
@arg("exp", type=int)
def pow(base, exp):
    print(base**exp)


if __name__ == "__main__":
    main()
