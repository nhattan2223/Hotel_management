"""Test security utilities."""
from utils.security import hash_password, verify_password


class TestSecurity:
    def test_hash_and_verify(self):
        pw = "123456"
        hashed = hash_password(pw)
        assert ":" in hashed
        assert verify_password(pw, hashed)

    def test_wrong_password(self):
        hashed = hash_password("correct")
        assert not verify_password("wrong", hashed)

    def test_empty_password(self):
        hashed = hash_password("")
        assert verify_password("", hashed)

    def test_invalid_hash_format(self):
        assert not verify_password("test", "invalidhash")
        assert not verify_password("test", "")
