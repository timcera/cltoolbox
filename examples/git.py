from cltoolbox import arg, command, main


@command
@arg("force", "--force", "-f")
@arg("dry_run", "--dry_run", "-n")
def push(repository, all=False, dry_run=False, force=False, thin=False):
    """Update remote refs along with associated objects.

    :param repository: Repository to push to.
    :param all: Push all refs.
    :param dry_run: Dry run.
    :param force: Force updates.
    :param thin: Use thin pack.
    """
    print(
        f"Pushing to {repository}. All: {all}, dry run: {dry_run}, force: {force}, thin: {thin}"
    )


if __name__ == "__main__":
    main()
