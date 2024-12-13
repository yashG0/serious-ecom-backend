from passlib.context import CryptContext

pass_context = CryptContext(schemes="bcrypt")


def hash_password(passwd: str) -> str:
    return pass_context.hash(passwd)


def verify_password(passwd: str, hash_passwd: str) -> bool:
    return pass_context.verify(passwd, hash_passwd)
