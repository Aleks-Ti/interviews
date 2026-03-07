from dataclasses import dataclass
from os import getenv
from pathlib import Path

from sqlalchemy.engine import URL

BASE_DIR_PROJECT = Path(__file__).resolve().parent.parent.parent
"""
project/                  < - указывает BASE_DIR_PROJECT
├── pyproject.toml
├── README.md
├── .gitignore
├── ... прочее
├── src/                  # Основная директория для кодовой базы проекта
│   └── main.py           # Основной файл приложения
│   └── __init__.py
│   └── <другие модули и файлы проекта>
└── tests/                # Директория с тестами
    └── __init__.py       # Индикатор пакета для тестов
"""


@dataclass
class PostgresDatabaseConfig:
    name: str | None = getenv("PG_DB")
    user: str | None = getenv("PG_USER")
    passwd: str | None = getenv("PG_PASSWORD", None)
    port: int = int(getenv("PG_PORT", 5432))
    host: str = getenv("PG_HOST", "db")

    driver: str = "asyncpg"
    sync_driver: str = "psycopg2"
    database_system: str = "postgresql"

    def __post_init__(self):
        required_vars = ["name", "user", "passwd", "port", "host"]
        for var in required_vars:
            value = getattr(self, var)
            if value is None:
                raise ValueError(f"Environment variable for {var} is not set")

    def build_connection_str(self) -> str:
        return URL.create(
            drivername=f"{self.database_system}+{self.driver}",
            username=self.user,
            database=self.name,
            password=self.passwd,
            port=self.port,
            host=self.host,
        ).render_as_string(hide_password=False)

    def sync_build_connection_str(self) -> str:
        return URL.create(
            drivername=f"{self.database_system}+{self.sync_driver}",
            username=self.user,
            database=self.name,
            password=self.passwd,
            port=self.port,
            host=self.host,
        ).render_as_string(hide_password=False)


@dataclass
class TokenConfig:
    default_encoding: str = "utf-8"
    hmac_digest_mode: str = "sha256"
    jwt_sign_algorithm: str = "HS256"
    secret_key: str = getenv("TOKEN_SECRET_KEY")
    access_token_expire_minutes: int = 12 * 60
    """
    now installed = 12 * 60 = 720 minutes 12 hours
    x * y = token lifetime, where x = your operand, y = N minutes.
    """

    def __post_init__(self):
        required_vars = ["secret_key"]
        for var in required_vars:
            value = getattr(self, var)
            if value is None:
                raise ValueError(f"Environment variable for {var} is not set")


@dataclass
class Configuration:
    debug = bool(getenv("DEBUG"))
    secure_cookie = not bool(getenv("SECURE_COOKIE"))
    db = PostgresDatabaseConfig()
    token = TokenConfig()


conf = Configuration()
