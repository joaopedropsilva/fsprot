import os
import subprocess
import tempfile
import itertools

from crypto import NaclBinder
from header import FileHeader


class File:
    _CAP_PRIVILEGED_BIN_PATH = "/usr/local/lib/fsprot/cap"

    @staticmethod
    def assert_ownership(file: str) -> None:
        file_stat = os.stat(file)
        current_uid = os.geteuid()

        assert file_stat.st_uid == current_uid, "Must file file owner to use this command."

    @staticmethod
    def get_metadata(file: str) -> dict:
        is_bin_file = False
        is_protected = False
        try:
            with open(file, "rb") as f:
                while chunk := f.read(4096):
                    txt_content = chunk.decode("utf-8")
                    if b"\x00" in chunk:
                        is_bin_file = True
                    is_protected = FileHeader.check_if_header_exists(txt_content)
        except UnicodeDecodeError:
            is_bin_file = True

        return {
            "mode": os.stat(file).st_mode,
            "type": "bin" if is_bin_file else "txt",
            "is_protected": is_protected
        }

    @staticmethod
    def get_write_mode_and_content(file_type: str, file_bytes: bytes) -> tuple[str, bytes | str]:
        write_mode = "wb"
        content = file_bytes
        if file_type == "txt":
            write_mode = "w"
            content = file_bytes.decode("utf-8")

        return write_mode, content

    @staticmethod
    def rewrite_protected(file: str, file_key: bytes, header: str) -> None:
        file_content = None
        with open(file, "rb") as f:
            file_content = f.read()

        encrypted_as_text = header
        encrypted_as_text += \
            NaclBinder.b64_encrypt(file_key, file_content).decode("utf-8")
        encrypted_as_text += "\n"

        file_dir = os.path.dirname(file)
        fd, tmp_path = tempfile.mkstemp(dir=file_dir)
        try:
            with os.fdopen(fd, "w") as temp:
                temp.write(encrypted_as_text)
                temp.flush()
                os.fsync(temp.fileno())

            os.rename(tmp_path, file)
        except Exception:
            os.unlink(tmp_path)

    @staticmethod
    def _get_ciphertext(file: str) -> str:
        read_start = FileHeader.HEADER_SIZE
        with open(file) as f:
            try:
                return list(itertools.islice(f, read_start, None))[0].strip()
            except IndexError:
                raise Exception("No ciphertext found for the file.")
            except Exception as err:
                raise Exception(f"Unable to read file ciphertext: {err}")

    @classmethod
    def access_protected(cls, file: str, pwd_bytes: bytes) -> tuple[dict, bytes]:
        header_info = FileHeader.get_header_info(file, pwd_bytes)
        file_key = header_info["file_key"]

        ciphertext = cls._get_ciphertext(file)

        return header_info, NaclBinder.b64_decrypt(file_key, ciphertext)

    @classmethod
    def _call_capable_write_script(cls, file: str, passphrase: str, content: str) -> None:
        subprocess.run([cls._CAP_PRIVILEGED_BIN_PATH, file, passphrase, content])

    @classmethod
    def write_protected(cls,
                        file: str,
                        passphrase: str,
                        header_info: dict,
                        content_bytes: bytes) -> None:
        file_key = header_info["file_key"]

        new_content = header_info["header_str"]

        protected_bytes = NaclBinder.b64_encrypt(file_key, content_bytes)
        new_content += protected_bytes.decode("utf-8")

        cls._call_capable_write_script(file, passphrase, new_content)
