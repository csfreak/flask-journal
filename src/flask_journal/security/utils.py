import secrets

from flask_security import hash_password

PASSWORD_LENGTH: int = 8  # This will be overwritten by SECURITY_PASSWORD_LENGTH_MIN


def get_random_pw_hash() -> str:
    return hash_password(secrets.token_urlsafe(PASSWORD_LENGTH))
