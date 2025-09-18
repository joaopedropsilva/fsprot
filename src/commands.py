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


def _assert_file_ownership(file: str) -> None:
    file_stat = os.stat(file)
    current_uid = os.geteuid()

    assert file_stat.st_uid == current_uid, "Must file file owner to use this command."


def _handle_output_arg(output: str | TextIOWrapper | None, file_bytes: bytes) -> None:
    file_str = file_bytes.decode("utf-8")
    if isinstance(output, TextIOWrapper):
        output.write(file_str)
        exit()

    with open(output, "w") as f:
        f.write(file_str)

    exit()


def protect(file: str, rotate: bool) -> None:
    _assert_file_ownership(file)

    _, pwd_bytes = _prompt_for_passphrase()

    file_key = NaclBinder.b64_keygen()

    header = FileHeader.gen_header(file, pwd_bytes, file_key)
    File.rewrite_protected(file, file_key, header)

    current_mode = os.stat(file).st_mode
    os.chmod(file, current_mode | S_IROTH)


def access(file: str, output: str | TextIOWrapper | None) -> None:
    passphrase, pwd_bytes = _prompt_for_passphrase()

    header_info, file_bytes = File.access_protected(file, pwd_bytes)

    _handle_output_arg(output, file_bytes)

    new_bytes = file_bytes

    File.write_protected(file, passphrase, header_info, new_bytes)

def unprotect(file: str) -> None:
    _assert_file_ownership(file)

    _, pwd_bytes = _prompt_for_passphrase()

    _, file_bytes = File.access_protected(file, pwd_bytes)

    with open(file, "w") as f:
        f.write(file_bytes.decode("utf-8"))
