from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class RoleName(StrEnum):
    admin = "admin"
    user = "user"


@dataclass
class Role:
    id: int
    name: str


@dataclass
class User:
    id: UUID
    email: str
    role: Role
    is_active: bool
    date_create: datetime
    date_update: datetime
