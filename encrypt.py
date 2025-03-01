import os
import json
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import datetime
from typing import Union

class CryptoKey:
    def __init__(self, raw: bytes, algorithm: str, extractable: bool, usages: list):
        self.raw = raw
        self.algorithm = algorithm
        self.extractable = extractable
        self.usages = usages

class EncryptionManager:
    @staticmethod
    def import_key() -> CryptoKey:
        try:
            n = "29E9648DAF0C".encode('utf-8')
            return CryptoKey(raw=n, algorithm="PBKDF2", extractable=False, usages=["deriveKey"])
        except Exception as e:
            raise Exception(f"Error importing key: {str(e)}")

    @staticmethod
    def encrypt(n: Union[CryptoKey, bytes], human_text: str) -> str:
        try:
            a = bytearray(os.urandom(12))
            o = n.raw if isinstance(n, CryptoKey) else n
            s = json.dumps({"human": human_text, "timestamp": datetime.datetime.now().isoformat()}).encode('utf-8')
            aesgcm = AESGCM(o)
            l = aesgcm.encrypt(bytes(a), s, None)
            j_str = json.dumps({
                "iv": list(a),
                "data": list(l)
            })
            t = j_str.encode('utf-8')
            return base64.b64encode(t).decode('utf-8')
        except Exception as e:
            raise Exception(f"Encryption failed: {str(e)}")

    @staticmethod
    def derive_key(t: Union[CryptoKey, bytes]) -> CryptoKey:
        try:
            n = t.raw if isinstance(t, CryptoKey) else t
            salt = bytes([0] * 16)
            iterations = 100000
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=iterations,
                backend=default_backend()
            )
            password = n if isinstance(n, bytes) else n
            derived_bytes = kdf.derive(password)
            return CryptoKey(raw=derived_bytes, algorithm="AES-GCM", extractable=True, usages=["encrypt", "decrypt"])
        except Exception as e:
            raise Exception(f"Key derivation failed: {str(e)}") 