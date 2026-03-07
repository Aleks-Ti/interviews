from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class Role:
    id: int
    name: str


@dataclass
class User:
    id: UUID
    email: str
    role: Role
    password: str
    is_active: bool
    date_create: datetime
    date_update: datetime
