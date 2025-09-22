import sys
import getpass
from io import TextIOWrapper

from crypto import NaclBinder
from file import File
from header import FileHeader


def _prompt_for_passphrase() -> tuple[str, bytes]:
    passphrase = getpass.getpass(
            "Type a passphrase to protect the file\n"
            "WARNING: you will not be able to recover the file contents without the passphrase!\n"
            "Passphrase: ")
    return passphrase, passphrase.encode("utf-8")


def _handle_output_arg(file_data: dict, output: str | TextIOWrapper | None) -> None:
    file_type = file_data["type"]
    file_mode = file_data["mode"]
    file_bytes = file_data["file_bytes"]

    write_mode = File.get_write_mode_by_type(file_type)
    content = File.get_content_by_type(file_type, file_bytes)

    if isinstance(output, TextIOWrapper):
        if file_type == "bin":
            sys.stderr.write("Cannot write binary file to stdout.\n")
            exit(1)

        output.write(content)

        exit()

    with open(output, write_mode) as f:
        f.write(content)

    File.restore_file_mode(output, file_mode)

    exit()


def protect(file: str, rotate: bool) -> None:
    File.assert_ownership(file)

    file_meta = File.get_metadata(file)

    if file_meta["is_protected"]:
        print("File is already protected by fsprot.")
        exit(1)

    _, pwd_bytes = _prompt_for_passphrase()

    file_key = NaclBinder.b64_keygen()

    file_data = {
        "file": file,
        "file_key": file_key,
        "meta": {**file_meta}
    }

    header = FileHeader.gen_header(file_data, pwd_bytes)

    File.rewrite_protected(file, file_key, header)

    File.set_mode_0644(file)


def access(file: str, output: str | TextIOWrapper | None) -> None:
    file_meta = File.get_metadata(file)
    if not file_meta["is_protected"]:
        sys.stderr.write("Cannot \"access\" an unprotected file.\n")
        exit(1)

    passphrase, pwd_bytes = _prompt_for_passphrase()

    header_info, file_bytes = File.access_protected(file, pwd_bytes)

    file_data = {
        "type": file_meta["type"],
        "mode": file_meta["mode"],
        "file_bytes": file_bytes
    }
    _handle_output_arg(file_data, output)

    new_bytes = file_bytes

    File.write_protected(file, passphrase, header_info, new_bytes)


def unprotect(file: str) -> None:
    File.assert_ownership(file)

    file_meta = File.get_metadata(file)

    if not file_meta["is_protected"]:
        sys.stderr.write("Cannot \"unprotect\" an unprotected file.\n")
        exit(1)

    _, pwd_bytes = _prompt_for_passphrase()

    _, file_bytes = File.access_protected(file, pwd_bytes)

    write_mode = File.get_write_mode_by_type(file_meta["type"])
    content = File.get_content_by_type(file_meta["type"], file_bytes)

    with open(file, write_mode) as f:
        f.write(content)

    File.restore_file_mode(file, file_meta["mode"])
