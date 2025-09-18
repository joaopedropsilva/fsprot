import argparse
import sys
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

    parser.add_argument("file", help="The file which a command will run on.")
    parser.add_argument("--protect",
                        "-p",
                        action="store_true",
                        help="Protects a file by encryption with a key derived from a passphrase.")
    parser.add_argument("--access",
                        "-a",
                        action="store_true",
                        help="Access a protected file by opening it on the default $EDITOR or "
                            "outputs the file content if used with --output argument.")
    parser.add_argument("--unprotect",
                        "-u",
                        action="store_true",
                        help="Remove file protection by writing back its original content.")
    parser.add_argument("--rotate",
                        "-r",
                        action="store_true",
                        help="Must be used with --protect option to rotate file encryption key.")
    parser.add_argument("--output",
                        "-o",
                        help="Must be used with --access to specify a file to write a decryption output. "
                            "If no file is specified the stdout is assumed.",
                        nargs="?",
                        const=sys.stdout,
                        default=None)
    args = parser.parse_args()

    assert os.path.isfile(args.file), f"File \"{args.file}\" does not exist."

    if args.protect:
        protect(args.file, args.rotate)
    elif args.access:
        access(args.file, args.output)
    elif args.unprotect:
        pass


if __name__ == "__main__":
    catch_exceptions(cli_main)
