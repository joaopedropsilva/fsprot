import os

from .crypto import NaclBinder


class File:
    APP_NAME = "FSPROT"
    
    @staticmethod
    def _build_mac(file: str, salt_bytes: bytes, file_key: bytes) -> bytes:
        file_realpath = os.path.realpath(file)
        salt = salt_bytes.decode("utf-8")
        mac_message = f"{file_realpath}-{salt}".encode("utf-8")

        return NaclBinder.b64_gen_mac(mac_message, file_key)

    @classmethod
    def _get_header_markers(cls) -> tuple[str, str]:
        start = "=" * 20 + f"{cls.APP_NAME} PROTECTED FILE HEADER" + "=" * 20
        end = "=" * len(start) + "\n"

        return start, end

    @classmethod
    def _build_header_string(cls, file_mac: bytes, salt: bytes, sealed_fk: bytes) -> str:
        start_marker, end_marker = cls._get_header_markers()

        header = start_marker
        header += \
            f"\nFILE_MAC={file_mac.decode('utf-8')}\n" \
            f"SALT={salt.decode('utf-8')}\n" \
            f"SEALED_FK={sealed_fk.decode('utf-8')}\n"
        header += end_marker

        return header

    @classmethod
    def gen_header(cls, file: str, pwd_bytes: bytes, file_key: bytes) -> str:
        sealing_key, salt = NaclBinder.derive_key_from_password(pwd_bytes)
        sealed_fk = NaclBinder.b64_encrypt(sealing_key, file_key)

        file_mac = cls._build_mac(file, salt, file_key)

        return cls._build_header_string(file_mac, salt, sealed_fk)

