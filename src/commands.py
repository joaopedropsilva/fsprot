import os
import pwd
import grp
import getpass
from stat import S_IROTH
from io import TextIOWrapper

from crypto import NaclBinder
from file import File
from header import FileHeader


def protect(file: str, rotate: bool) -> None:
    file_stat = os.stat(file)
    current_uid = os.geteuid()

    assert file_stat.st_uid == current_uid, "Must file file owner to use this command."

    passphrase = getpass.getpass(
            "Type a passphrase to protect the file\n"
            "WARNING: you will not be able to recover the file contents without the passphrase!\n"
            "Passphrase: ")
    pwd_bytes = passphrase.encode("utf-8")

    file_key = NaclBinder.b64_keygen()

    header = FileHeader.gen_header(file, pwd_bytes, file_key)
    File.rewrite_protected(file, file_key, header)

    current_mode = file_stat.st_mode
    os.chmod(file, current_mode | S_IROTH)


def access(file: str, output: str | TextIOWrapper | None) -> None:
    passphrase = getpass.getpass(
            "Type a passphrase to protect the file\n"
            "WARNING: you will not be able to recover the file contents without the passphrase!\n"
            "Passphrase: ")
    pwd_bytes = passphrase.encode("utf-8")

    header_info, file_bytes = File.access_protected(file, pwd_bytes)

    # no updates for now
    new_bytes = file_bytes

    File.write_protected(file, passphrase, header_info, new_bytes)
