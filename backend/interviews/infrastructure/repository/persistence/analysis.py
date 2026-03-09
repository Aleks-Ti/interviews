from sqlalchemy import select

from interviews.domain.analysis.models import Analysis as DomainAnalysis
from interviews.domain.analysis.repository import AnalysisRepository
from interviews.infrastructure.database.models.analysis import Analysis as OrmAnalysis
from interviews.infrastructure.repository.base_repository import BaseImplementationRepository


class PostgresAnalysisRepository(BaseImplementationRepository[OrmAnalysis, DomainAnalysis], AnalysisRepository):
    model: type[OrmAnalysis] = OrmAnalysis

    def _to_domain(self, orm_obj: OrmAnalysis) -> DomainAnalysis:
        return DomainAnalysis(
            id=orm_obj.id,
            score=orm_obj.score,
            summary=orm_obj.summary,
            strengths=orm_obj.strengths,
            weaknesses=orm_obj.weaknesses,
            recommendation=orm_obj.recomendation,  # typo in DB column kept as-is
            answer_id=orm_obj.answer_id,
        )

    async def find_by_answer_id(self, answer_id: int) -> DomainAnalysis | None:
        stmt = select(self.model).where(self.model.answer_id == answer_id)
        res = await self._session.execute(stmt)
        orm_obj = res.scalar_one_or_none()
        if orm_obj is None:
            return None
        return self._to_domain(orm_obj)
