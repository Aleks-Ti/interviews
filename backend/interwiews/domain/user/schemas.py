from datetime import datetime
from uuid import UUID

from pydantic import Field, field_validator

from interwiews.common.exceptions import UnprocessableEntity
from interwiews.common.schemas import PreBasePydanticModel


def password_validate(value: str) -> str:
    UnprocessableEntity(len(value) >= 8, "Password must be at least 8 characters")
    UnprocessableEntity(any(char.isupper() for char in value), "Password must contain at least one uppercase letter")
    UnprocessableEntity(any(char.islower() for char in value), "Password must contain at least one lowercase letter")
    UnprocessableEntity(any(char.isdigit() for char in value), "Password must contain at least one digit")
    UnprocessableEntity(any(not char.isalnum() for char in value), "Password must contain at least one special character")
    return value


class GetRoleSchema(PreBasePydanticModel):
    id: int
    name: str


class GetUserSchema(PreBasePydanticModel):
    id: UUID | int
    email: str
    role: GetRoleSchema
    is_active: bool
    date_create: datetime
    date_update: datetime
    is_allowed_comment: bool


class UserFilters(PreBasePydanticModel):
    page: int = Field(ge=1, default=1)
    page_size: int = Field(ge=1, default=20)
    sort_date_joined: bool = Field(
        True, description="Sort users by date_joined. Where False == ASC, True == DESC, None/-- == no impact"
    )
    is_active: bool | None = Field(
        None,
        description=(
            "ADMIN ACCESS. Фильтрация users по is_active.  Где True, т.е активный,"
            " False, не активный пользователь, т.е. забанненый, а None/-- влияние параметра на запрос - отсутствует."
        ),
    )


class CreateUserSchema(PreBasePydanticModel):
    email: str = Field(examples=["your.email@domain.code"])
    password: str = Field(examples=["I-am-BREAD!+1"])
    role_id: int

    @field_validator("password")
    def password_complexity(cls, value: str) -> str:
        return password_validate(value)


class ChangePasswordUserSchema(PreBasePydanticModel):
    user_id: UUID | int = Field(examples=["UUID_пользователя_для_которого_нужно_изменить_пароль"])
    password: str = Field(examples=["I-am-BREAD!+1"])

    @field_validator("password")
    def password_complexity(cls, value: str) -> str:
        return password_validate(value)
