import os
import signal
import hashlib
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization


def get_working_dir(d = None) -> str:
    """
    get working directory's root
    return -- absolute dir of working dir's root
    """

    if hasattr(get_working_dir, 'cache'):
        return get_working_dir.cache

    if d is None:
        d = os.getcwd()
    while os.path.dirname(d) != d:
        if os.path.isdir(os.path.join(d, ".datagit")):
            break
        d = os.path.dirname(d)

    if os.path.dirname(d) != d:
        get_working_dir.cache = d
        return d
    else:
        return None


def get_hash(file: str) -> str:
    data = ""
    with open(file, 'rb') as f:
        data = f.read()
    return hashlib.sha1(data).hexdigest()


def in_working_dir(dir: str) -> bool:
    working_dir = get_working_dir()
    working_dir = os.path.abspath(working_dir)
    dir = os.path.abspath(dir)
    if len(working_dir) > len(dir):
        return False
    dir = dir[:len(working_dir)]
    if dir != working_dir:
        return False
    return True


def init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def encrypt(msg: bytes, public_key: rsa.RSAPublicKey) -> bytes:
    return public_key.encrypt(
        msg,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        )
    )


def decrypt(ciphertext: bytes, private_key: rsa.RSAPrivateKey) -> bytes:
    return private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        )
    )


def load_public_key(filename: str) -> rsa.RSAPublicKey:
    with open(filename, "rb") as f:
        return serialization.load_ssh_public_key(f.read())


def load_private_key(filename: str, passwd: bytes=b''):
    with open(filename, "rb") as f:
        return serialization.load_ssh_private_key(f.read(), password=passwd)