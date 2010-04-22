from hashlib import sha256


def encrypt_password(password):
    h = sha256()
    h.update(password)
    return h.hexdigest()
