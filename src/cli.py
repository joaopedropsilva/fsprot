import argparse
import os

from commands import protect, access


DESCRIPTION="""
A command line tool that enables file content protection by encryption.
"""


def catch_exceptions(function: callable) -> None:
    try:
        function()
    except Exception as err:
        print(err)


def cli_main() -> None:
    parser = argparse.ArgumentParser(
        prog="fsprot",
        description=DESCRIPTION
    )

    parser.add_argument("command")
    parser.add_argument("file")
    args = parser.parse_args()

    assert os.path.isfile(args.file), f"File \"{args.file}\" does not exist."

    if args.command == "protect":
        protect(args.file)
    elif args.command == "access":
        access(args.file)
    else:
        # print known commands
        print("Unknown command.")


if __name__ == "__main__":
    catch_exceptions(cli_main)
