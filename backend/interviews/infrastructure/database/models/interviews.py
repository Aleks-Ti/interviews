from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from interviews.infrastructure.database.base_model import Base


class Interviews(Base):
    __tablename__ = "interviews"

    id: Mapped[int] = mapped_column(sa.BigInteger, primary_key=True, nullable=False, unique=True)
    candidate_name: Mapped[str] = mapped_column(sa.String(256), unique=False, nullable=False)
    type: Mapped[str] = mapped_column(sa.String(64), unique=False, nullable=False)
    status: Mapped[str] = mapped_column(sa.String(64), unique=False, nullable=False)
    date_create = mapped_column(
        sa.DateTime(timezone=True),
        unique=False,
        nullable=False,
        default=sa.func.now(),
    )
    date_update = mapped_column(
        sa.DateTime(timezone=True),
        unique=False,
        nullable=False,
        default=sa.func.now(),
        onupdate=sa.func.now(),
    )

    conducted_by: Mapped[UUID] = mapped_column(sa.UUID, sa.ForeignKey("users.id"), unique=False, nullable=False)
    plan_id: Mapped[int] = mapped_column(sa.ForeignKey("plans.id"), nullable=False, unique=False)

    plan = relationship("Plans", back_populates="interviews")
    conducted_by_user = relationship("Users", back_populates="interviews")
    answers = relationship("Answers", back_populates="interview")
