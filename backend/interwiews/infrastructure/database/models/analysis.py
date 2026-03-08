import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from interwiews.infrastructure.database.base_model import Base


class Analysis(Base):
    __tablename__ = "analysis"

    id: Mapped[int] = mapped_column(sa.BigInteger, primary_key=True, nullable=False, unique=True)
    score: Mapped[float] = mapped_column(sa.Float, unique=False, nullable=False)
    summary: Mapped[str] = mapped_column(sa.Text, unique=False, nullable=True)
    strengths: Mapped[list] = mapped_column(sa.JSON, unique=False, nullable=True)
    weaknesses: Mapped[list] = mapped_column(sa.JSON, unique=False, nullable=True)
    recomendation: Mapped[str] = mapped_column(sa.Text, unique=False, nullable=True)

    answer_id: Mapped[int] = mapped_column(sa.ForeignKey("answers.id"), nullable=False, unique=False)

    answer = relationship("Answers", back_populates="analysis")
