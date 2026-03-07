from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any, Generic, Protocol, TypeVar
from uuid import UUID

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import InstrumentedAttribute

from interwiews.common.exceptions import ItemNotExist


class HasId(Protocol):
    id: Any


T = TypeVar("T", bound=HasId)
TOrmModel = TypeVar("TOrmModel", bound=HasId)
TDomainModel = TypeVar("TDomainModel", bound=HasId)


class AbstractRepository(ABC, Generic[T]):
    @abstractmethod
    async def add_one(self, data: dict) -> T:
        raise NotImplementedError

    @abstractmethod
    async def find_one(self, item_id: int | UUID) -> T:
        raise NotImplementedError

    @abstractmethod
    async def find_all(self) -> Sequence[T]:
        raise NotImplementedError

    @abstractmethod
    async def update_one(self, item_id: int | UUID, data: dict) -> T:
        raise NotImplementedError

    @abstractmethod
    async def delete_one(self, item_id: int | UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    async def find_one_or_none(self, item_id: int | UUID) -> T | None:
        raise NotImplementedError


class BaseImplementationRepository(AbstractRepository[TDomainModel], Generic[TOrmModel, TDomainModel]):
    model: type[TOrmModel]

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @abstractmethod
    def _to_domain(self, orm_obj: TOrmModel) -> TDomainModel:
        raise NotImplementedError

    def _to_domain_many(self, orm_objs: Sequence[TOrmModel]) -> list[TDomainModel]:
        return [self._to_domain(obj) for obj in orm_objs]

    async def get_all_columns_model(self, model) -> list[InstrumentedAttribute]:
        return [getattr(model, column.name) for column in model.__table__.c]

    async def add_one(self, data: dict) -> TDomainModel:
        stmt = insert(self.model).values(**data).returning(self.model)
        res = await self._session.execute(stmt)
        orm_obj = res.scalar_one()
        return self._to_domain(orm_obj)

    async def find_one(self, item_id: int | UUID) -> TDomainModel:
        stmt = select(self.model).where(self.model.id == item_id)
        res = await self._session.execute(stmt)
        return self._to_domain(res.scalar_one())

    async def find_all(self) -> Sequence[TDomainModel]:
        stmt = select(self.model)
        res = await self._session.execute(stmt)
        return self._to_domain_many(res.scalars().all())

    async def update_one(self, item_id: int | UUID, data: dict) -> TDomainModel:
        stmt = update(self.model).where(self.model.id == item_id).values(**data).returning(self.model)
        res = await self._session.execute(stmt)
        orm_obj = res.scalar_one()
        return self._to_domain(orm_obj)

    async def delete_one(self, item_id: int | UUID) -> None:
        stmt = delete(self.model).where(self.model.id == item_id)
        res = await self._session.execute(stmt)
        if res.rowcount == 0:
            raise ItemNotExist

    async def update_all(self, data: dict) -> Sequence[TDomainModel]:
        stmt = update(self.model).values(**data).returning(self.model)
        res = await self._session.execute(stmt)
        return self._to_domain_many(res.scalars().all())

    async def find_one_or_none(self, item_id: int | UUID) -> TDomainModel | None:
        stmt = select(self.model).where(self.model.id == item_id)
        res = await self._session.execute(stmt)
        orm_obj = res.scalar_one_or_none()
        if orm_obj is None:
            return None
        return self._to_domain(orm_obj)
