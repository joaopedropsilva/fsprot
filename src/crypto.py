from nacl import pwhash, secret, utils, encoding
from nacl.hash import blake2b


class NaclBinder:
    KDF = pwhash.argon2i.kdf
    OPS = pwhash.argon2i.OPSLIMIT_SENSITIVE
    MEM = pwhash.argon2i.MEMLIMIT_SENSITIVE

    @staticmethod
    def b64_keygen() -> bytes:
        key = utils.random(secret.SecretBox.KEY_SIZE)
        return encoding.Base64Encoder.encode(key)

    @staticmethod
    def b64_gen_mac(message: bytes, b64_key: bytes) -> bytes:
        key = encoding.Base64Encoder.decode(b64_key)
        return blake2b(message, key=b64_key, encoder=encoding.Base64Encoder)

    @staticmethod
    def b64_encrypt(b64key: bytes, data: bytes) -> bytes:
        box = secret.SecretBox(b64key, encoder=encoding.Base64Encoder)
        return encoding.Base64Encoder.encode(box.encrypt(data))

    @staticmethod
    def b64_decrypt(b64key: bytes, data: bytes) -> bytes:
        box = secret.SecretBox(b64key, encoder=encoding.Base64Encoder)
        return box.decrypt(data)

    @classmethod
    def _b64_derive(cls, pwd: bytes, salt: bytes) -> bytes:
        derived_key = cls.KDF(secret.SecretBox.KEY_SIZE, pwd, salt, opslimit=cls.OPS, memlimit=cls.MEM)
        return encoding.Base64Encoder.encode(derived_key)

    @classmethod
    def derive_key_from_password(cls, pwd: bytes, b64_salt: bytes = None) -> tuple[bytes, bytes]:
        if not b64_salt:
            salt = utils.random(pwhash.argon2i.SALTBYTES)

            return cls._b64_derive(pwd, salt), encoding.Base64Encoder.encode(salt)

        salt = encoding.Base64Encoder.decode(b64_salt)

        return cls._b64_derive(pwd, salt), b64_salt

