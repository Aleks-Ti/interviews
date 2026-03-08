import uuid

import sqlalchemy as sa
from sqlalchemy.orm import mapped_column, relationship

from interwiews.infrastructure.database.base_model import Base


class Users(Base):
    __tablename__ = "users"

    id = mapped_column(sa.UUID, primary_key=True, unique=True, nullable=False, default=uuid.uuid4)
    password = mapped_column(sa.String(512), unique=False, nullable=False)
    email = mapped_column(sa.String(64), unique=True, nullable=False)
    role_id = mapped_column(sa.Integer, sa.ForeignKey("roles.id", ondelete="CASCADE"), unique=False, nullable=False)
    is_active = mapped_column(sa.Boolean, unique=False, nullable=False, default=True)
    date_create = mapped_column(sa.DateTime(timezone=True), unique=False, nullable=False, default=sa.func.now())
    date_update = mapped_column(
        sa.DateTime(timezone=True), unique=False, nullable=False, default=sa.func.now(), onupdate=sa.func.now()
    )

    role = relationship("Roles", back_populates="users")
    interviews = relationship("Interviews", back_populates="conducted_by_user")


class Roles(Base):
    __tablename__ = "roles"

    id = mapped_column(sa.Integer, primary_key=True, unique=True, nullable=False)
    name = mapped_column(sa.String(64), unique=True, nullable=False)

    users = relationship("Users", back_populates="role")
