from abc import ABC, abstractmethod
from typing import Any, Generic, Protocol, TypeVar

import httpx


class HasId(Protocol):
    id: int


T = TypeVar("T", bound=HasId)


class AbstractApiClient(ABC, Generic[T]):
    @abstractmethod
    async def post_one(self, path: str, data: dict) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def get_all(self, path: str, query_params: dict) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def get_one(self, path: str, path_id: int) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def delete_one(self, path: str, path_id: int) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def patch_one(
        self,
        path: str,
        path_id: int,
        data: dict,
    ) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def update_one(self, path: str, path_id: int, data: dict) -> Any:
        raise NotImplementedError


class ApiClient(AbstractApiClient[T]):
    async def post_one(self, path: str, data: dict) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            response = await client.post(path, json=data)
            response.raise_for_status()
            return response

    async def get_all(self, path: str, query_params: dict) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            response: httpx.Response = await client.get(path, params=query_params)
            response.raise_for_status()
            return response

    async def get_one(self, path: str, path_id: int) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            url_with_path_id = f"{path}/{path_id}"
            response: httpx.Response = await client.get(url_with_path_id)
            response.raise_for_status()
            return response

    async def delete_one(self, path: str, path_id: int) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            url_with_path_id = f"{path}/{path_id}"
            response: httpx.Response = await client.delete(url_with_path_id)
            response.raise_for_status()
            return response

    async def patch_one(self, path: str, path_id: int, data: dict) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            url_with_path_id = f"{path}/{path_id}"
            response: httpx.Response = await client.patch(url_with_path_id, json=data)
            response.raise_for_status()
            return response

    async def update_one(self, path: str, path_id: int, data: dict) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            url_with_path_id = f"{path}/{path_id}"
            response: httpx.Response = await client.put(url_with_path_id, json=data)
            response.raise_for_status()
            return response
