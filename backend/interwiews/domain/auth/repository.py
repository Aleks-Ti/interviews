from abc import ABC, abstractmethod

from interwiews.domain.auth.models import User


class AuthUserRepository(ABC):
    @abstractmethod
    async def find_by_email(self, user_email: str) -> User | None:
        raise NotImplementedError
