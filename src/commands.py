import os
import pwd
import grp
import getpass

from .crypto import NaclBinder
from .file import FileHeader, File


def protect(file: str) -> None:
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


def access(file: str) -> None:
    passphrase = getpass.getpass(
            "Type a passphrase to protect the file\n"
            "WARNING: you will not be able to recover the file contents without the passphrase!\n"
            "Passphrase: ")
    pwd_bytes = passphrase.encode("utf-8")

    # Implement interface
    print(File.access_protected(file, pwd_bytes).read())
