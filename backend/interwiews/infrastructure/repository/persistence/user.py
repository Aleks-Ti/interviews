from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from interwiews.domain.auth.models import Role as AuthRole
from interwiews.domain.auth.models import User as AuthUser
from interwiews.domain.auth.repository import AuthUserRepository
from interwiews.domain.user.models import Role as DomainRole
from interwiews.domain.user.models import User as DomainUser
from interwiews.domain.user.repository import UserRepository
from interwiews.domain.user.schemas import UserFilters
from interwiews.infrastructure.database.models.user import Role as OrmRole
from interwiews.infrastructure.database.models.user import User as OrmUser
from interwiews.infrastructure.repository.base_repository import BaseImplementationRepository


class PostgresUserRepository(BaseImplementationRepository[OrmUser, DomainUser], UserRepository):
    model: type[OrmUser] = OrmUser

    def _to_domain(self, orm_obj: OrmUser) -> DomainUser:
        return DomainUser(
            id=orm_obj.id,
            email=orm_obj.email,
            role=DomainRole(id=orm_obj.role.id, name=orm_obj.role.name),
            is_active=orm_obj.is_active,
            date_create=orm_obj.date_create,
            date_update=orm_obj.date_update,
            is_allowed_comment=orm_obj.is_allowed_comment,
        )

    async def find_all_by_filter(self, query_params: UserFilters) -> Sequence[DomainUser]:
        skip = (query_params.page - 1) * query_params.page_size
        stmt = select(self.model).options(selectinload(self.model.role))

        if query_params.is_active is not None:
            stmt = stmt.where(self.model.is_active == query_params.is_active)

        if query_params.sort_date_joined:
            stmt = stmt.order_by(self.model.date_create.desc())
        else:
            stmt = stmt.order_by(self.model.date_create.asc())

        stmt = stmt.limit(query_params.page_size).offset(skip)
        res = await self._session.execute(stmt)
        return self._to_domain_many(res.scalars().all())

    async def find_by_email(self, user_email: str) -> DomainUser | None:
        stmt = select(self.model).where(self.model.email == user_email).options(selectinload(self.model.role))
        res = await self._session.execute(stmt)
        orm_obj = res.scalar_one_or_none()
        if orm_obj is None:
            return None
        return self._to_domain(orm_obj)

    async def find_one(self, item_id: UUID | int) -> DomainUser:
        stmt = select(self.model).where(self.model.id == item_id).options(selectinload(self.model.role))
        res = await self._session.execute(stmt)
        return self._to_domain(res.scalar_one())

    async def update_one(self, item_id: int | UUID, data: dict) -> DomainUser:
        stmt = update(self.model).where(self.model.id == item_id).values(**data)
        await self._session.execute(stmt)
        return await self.find_one(item_id)

    async def find_one_or_none(self, item_id: UUID | int) -> DomainUser | None:
        stmt = select(self.model).where(self.model.id == item_id).options(selectinload(self.model.role))
        res = await self._session.execute(stmt)
        orm_obj = res.scalar_one_or_none()
        if orm_obj is None:
            return None
        return self._to_domain(orm_obj)

    async def update_all(self, data: dict) -> list[DomainUser]:
        stmt = update(self.model).values(**data).returning(self.model)
        res = await self._session.execute(stmt)
        return self._to_domain_many(res.scalars().all())


class PostgresAuthUserRepository(AuthUserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_email(self, user_email: str) -> AuthUser | None:
        stmt = select(OrmUser).where(OrmUser.email == user_email).options(selectinload(OrmUser.role))
        res = await self._session.execute(stmt)
        orm_obj = res.scalar_one_or_none()
        if orm_obj is None:
            return None
        return AuthUser(
            id=orm_obj.id,
            email=orm_obj.email,
            role=AuthRole(id=orm_obj.role.id, name=orm_obj.role.name),
            password=orm_obj.password,
            is_active=orm_obj.is_active,
            date_create=orm_obj.date_create,
            date_update=orm_obj.date_update,
        )
