import hmac
from datetime import UTC, datetime, timedelta

import bcrypt
from jose import jwt
from passlib.context import CryptContext

from interwiews.common.configuration import conf

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _pepper_password(password: str, salt: bytes, encoding: str = conf.token.default_encoding) -> bytes:
    bpwd = password.encode(encoding)
    pepper = conf.token.secret_key.encode(encoding)
    seasoned = hmac.new(pepper, msg=bpwd, digestmod=conf.token.hmac_digest_mode)
    seasoned.update(salt)
    return seasoned.digest()


def get_password_hash(password: str, encoding: str = conf.token.default_encoding) -> str:
    salt = bcrypt.gensalt()
    peppered = _pepper_password(password, salt)
    return bcrypt.hashpw(peppered, salt).decode(encoding)


def verify_password(plain_password: str, against: str, encoding: str = conf.token.default_encoding) -> bool:
    bsalt = against[:29].encode(encoding)
    peppered = _pepper_password(plain_password, bsalt)
    if bcrypt.checkpw(peppered, against.encode(encoding)):
        return True
    return False


def create_access_token(id: str) -> str:
    data: dict[str, str | datetime] = {"sub": id}
    expires_delta = timedelta(minutes=conf.token.access_token_expire_minutes)
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, conf.token.secret_key, algorithm=conf.token.jwt_sign_algorithm)
    return encoded_jwt


