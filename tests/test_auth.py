from wallet.auth import get_password_hash, verify_password_hash
from wallet.settings import settings


def test_verify_password_hash():
    assert verify_password_hash("1q2w3e", get_password_hash("1q2w3e"))


def test_salt():
    salt = "a" * settings.SALT_LENGTH
    assert get_password_hash("1q2w3e", salt)[: settings.SALT_LENGTH] == salt
