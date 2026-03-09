import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from interviews.infrastructure.database.base_model import Base


class Questions(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(sa.BigInteger, primary_key=True, nullable=False, unique=True)
    text: Mapped[str] = mapped_column(sa.Text, unique=False, nullable=False)
    type: Mapped[str] = mapped_column(sa.String(64), unique=False, nullable=False)
    criteria: Mapped[dict] = mapped_column(sa.JSON, unique=False, nullable=False)
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

    plan_id: Mapped[int] = mapped_column(sa.ForeignKey("plans.id", ondelete="CASCADE"), nullable=False, unique=False)

    plan = relationship("Plans", back_populates="questions", uselist=False)
    answer = relationship("Answers", back_populates="question", uselist=False, cascade="all, delete-orphan", passive_deletes=True)