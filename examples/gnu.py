# gnu.py
from cltoolbox import arg, command, main


@command
@arg("maxdepth", "-d", "--maxdepth", metavar="<levels>")
@arg("D", metavar="<debug-opt>")
def find(path, pattern, maxdepth=None, P=False, D=None):
    """Mock some features of the GNU find command.

    This is not at all a complete program, but a simple representation to
    showcase cltoolbox's coolest features.

    :param path: The starting path.
    :param pattern: The pattern to look for.
    :param int maxdepth: Descend at most <levels>.
    :param P: Do not follow symlinks.
    :param D: Debug option, print diagnostic information.
    """
    if maxdepth is not None and maxdepth < 2:
        print("If you choose maxdepth, at least set it > 1")
    if P:
        print("Following symlinks...")
    print(f"Debug options: {D}")
    print(f"Starting search with pattern: {pattern}")
    print("No file found!")


if __name__ == "__main__":
    main()
