import os
import tempfile
import itertools
from io import BytesIO

from .crypto import NaclBinder


class File:
    APP_NAME = "FSPROT"
    MAC_HEADER_MARKER = "FILE_MAC="
    SALT_HEADER_MARKER = "SALT="
    SEALED_FK_HEADER_MARKER = "SEALED_FK="
    HEADER_ATTR_DELIMITER = ";\n"
    
    @staticmethod
    def _build_mac(file: str, salt: str, file_key: bytes) -> str:
        file_realpath = os.path.realpath(file)
        mac_message = f"{file_realpath}-{salt}".encode("utf-8")

        return NaclBinder.b64_gen_mac(mac_message, file_key).decode("utf-8")

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

    @classmethod
    def _get_header_markers(cls) -> tuple[str, str]:
        start = "=" * 20 + f"{cls.APP_NAME} PROTECTED FILE HEADER" + "=" * 20 + "\n"
        end = "=" * len(start) + "\n"

        return start, end

    @classmethod
    def _build_header_string(cls, file_mac: str, salt: str, sealed_fk: str) -> str:
        start_marker, end_marker = cls._get_header_markers()

        header = start_marker
        header += \
            f"{cls.MAC_HEADER_MARKER}{file_mac}{cls.HEADER_ATTR_DELIMITER}" \
            f"{cls.SALT_HEADER_MARKER}{salt}{cls.HEADER_ATTR_DELIMITER}" \
            f"{cls.SEALED_FK_HEADER_MARKER}{sealed_fk}{cls.HEADER_ATTR_DELIMITER}"
        header += end_marker

        return header

    @classmethod
    def gen_header(cls, file: str, pwd_bytes: bytes, file_key: bytes) -> str:
        sealing_key, salt_bytes = NaclBinder.derive_key_from_password(pwd_bytes)
        salt = salt_bytes.decode("utf-8")
        sealed_fk = \
            NaclBinder.b64_encrypt(sealing_key, file_key).decode("utf-8")

        file_mac = cls._build_mac(file, salt, file_key)

        return cls._build_header_string(file_mac, salt, sealed_fk)

    @classmethod
    def _get_header(cls, file: str) -> tuple[str, int]:
        _, end_marker = cls._get_header_markers()

        header = ""
        end_line = 0
        with open(file) as f:
            for number, line in enumerate(f):
                header += line
                if line == end_marker:
                    end_line = number
                    break

        return header, end_line

    @classmethod
    def _parse_header(cls, file: str) -> dict:
        header_str, end_line = cls._get_header(file)

        header_attributes = [
            cls.MAC_HEADER_MARKER,
            cls.SALT_HEADER_MARKER,
            cls.SEALED_FK_HEADER_MARKER
        ]
        header_attr_values = []
        delim_start_pos = 0
        for attr in header_attributes:
            attr_pos = header_str.find(attr)
            if (attr_pos == -1):
                raise Exception("Invalid header: missing header attribute.")
            attr_pos = attr_pos + len(attr)

            delimiter_pos = header_str.find(cls.HEADER_ATTR_DELIMITER, delim_start_pos)
            if (delimiter_pos == -1):
                raise Exception("Invalid header: malformed delimiter.")

            header_attr_values.append(header_str[attr_pos:delimiter_pos])

            delim_start_pos = delimiter_pos + 1

        if len(header_attr_values) != len(header_attributes):
            raise Exception("Invalid header: failed to extract header values.")

        return {
            "file_mac": header_attr_values[0],
            "salt": header_attr_values[1],
            "sealed_fk": header_attr_values[2],
            "header_end": end_line
        }

    @staticmethod
    def _get_ciphertext_from_file(file: str, header_end: int) -> str:
        # Reads to EOF
        read_start = header_end + 1
        with open(file) as f:
            return list(itertools.islice(f, read_start, None))[0].strip()

    @classmethod
    def access_protected(cls, file: str, pwd_bytes: bytes) -> BytesIO:
        header = cls._parse_header(file)

        file_mac = header.get("file_mac")
        salt = header.get("salt")
        sealed_fk = header.get("sealed_fk")
        header_end = header.get("header_end")

        salt_bytes = salt.encode("utf-8")
        sealed_fk_bytes = sealed_fk.encode("utf-8")

        sealing_key, _ = NaclBinder.derive_key_from_password(pwd_bytes, salt_bytes)
        file_key = NaclBinder.b64_decrypt(sealing_key, sealed_fk_bytes)

        assert file_mac == cls._build_mac(file, salt, file_key), "Failed to validate file MAC."

        ciphertext = cls._get_ciphertext_from_file(file, header_end)

        return BytesIO(NaclBinder.b64_decrypt(file_key, ciphertext))
