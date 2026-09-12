from app.infrastructure.security.password import hash_password, verify_password


def test_hash_and_verify_password() -> None:
    hashed = hash_password("changeme")
    assert hashed != "changeme"
    assert verify_password("changeme", hashed)
    assert not verify_password("otra", hashed)
