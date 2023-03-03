import hashlib


def sha256_hash_hex(s: str) -> str:
    """
    Returns the hex digest of the SHA256 hash of the input string.
    :param s:
    :return:
    """
    m = hashlib.sha256()
    m.update(s.encode("utf-8"))
    return m.hexdigest()
