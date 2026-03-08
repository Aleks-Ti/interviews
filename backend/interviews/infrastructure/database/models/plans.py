import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from interviews.infrastructure.database.base_model import Base


class Plans(Base):
    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(sa.BigInteger, primary_key=True, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(sa.String(256), unique=False, nullable=False)
    description: Mapped[str] = mapped_column(sa.Text, unique=False, nullable=True)
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

    created_by_user_id: Mapped[sa.UUID] = mapped_column(sa.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False, unique=False)

    created_by_user = relationship("Users", back_populates="plans", foreign_keys=[created_by_user_id])
    questions = relationship("Questions", back_populates="plan")
    interviews = relationship("Interviews", back_populates="plan")
