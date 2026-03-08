import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from interviews.infrastructure.database.base_model import Base


class Answers(Base):
    __tablename__ = "answers"

    id: Mapped[int] = mapped_column(sa.BigInteger, primary_key=True, nullable=False, unique=True)
    answer: Mapped[str] = mapped_column(sa.Text, unique=False, nullable=False)
    audio_path: Mapped[str] = mapped_column(sa.String(256), unique=False, nullable=True)
    transcript: Mapped[str] = mapped_column(sa.Text, unique=False, nullable=True)
    date_create = mapped_column(
        sa.DateTime(timezone=True),
        unique=False,
        nullable=False,
        default=sa.func.now(),
    )
    date_update = mapped_column(
        sa.DateTime(timezone=True), unique=False, nullable=False, default=sa.func.now(), onupdate=sa.func.now()
    )

    question_id: Mapped[int] = mapped_column(sa.ForeignKey("questions.id"), nullable=False, unique=False)
    interview_id: Mapped[int] = mapped_column(sa.ForeignKey("interviews.id"), nullable=False, unique=False)

    question = relationship("Questions", back_populates="answers")  # noqa: F821
    interview = relationship("Interviews", back_populates="answers")
    analysis = relationship("Analysis", back_populates="answer", uselist=False)
