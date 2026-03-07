from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID


class RoleName(str, Enum):
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
    is_allowed_comment: bool
