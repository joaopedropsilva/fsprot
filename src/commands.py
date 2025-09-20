import os
import pwd
import grp
import getpass
from stat import S_IROTH
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


def _handle_output_arg(output: str | TextIOWrapper | None,
                       file_bytes: bytes,
                       file_type: str) -> None:
    write_mode, content = File.get_write_mode_and_content(file_type, file_bytes)

    if isinstance(output, TextIOWrapper):
        if file_type == "bin":
            print("Cannot write binary file to stdout.")
            exit(1)

        output.write(content)

        exit()

    with open(output, write_mode) as f:
        f.write(content)

    exit()


def protect(file: str, rotate: bool) -> None:
    File.assert_ownership(file)

    _, pwd_bytes = _prompt_for_passphrase()

    file_key = NaclBinder.b64_keygen()

    file_data = {
        "file": file,
        "file_key": file_key,
        **File.get_metadata(file)
    }

    header = FileHeader.gen_header(file_data, pwd_bytes)

    File.rewrite_protected(file, file_key, header)

    current_mode = file_data["meta"]["mode"]
    os.chmod(file, current_mode | S_IROTH)


def access(file: str, output: str | TextIOWrapper | None) -> None:
    passphrase, pwd_bytes = _prompt_for_passphrase()

    header_info, file_bytes = File.access_protected(file, pwd_bytes)

    _handle_output_arg(output, file_bytes, header_info["type"])

    new_bytes = file_bytes

    File.write_protected(file, passphrase, header_info, new_bytes)


def unprotect(file: str) -> None:
    File.assert_ownership(file)

    file_meta = File.get_metadata(file)

    _, pwd_bytes = _prompt_for_passphrase()

    header_info, file_bytes = File.access_protected(file, pwd_bytes)

    write_mode, content = File.get_write_mode_and_content(file_meta["type"], file_bytes)

    with open(file, write_mode) as f:
        f.write(content)
