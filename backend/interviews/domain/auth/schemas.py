from pydantic import Field

from interviews.core.schemas import PreBasePydanticModel


class LoginSuccessSchema(PreBasePydanticModel):
    message: str = Field(default="Login successful")


class LogoutSuccessSchema(PreBasePydanticModel):
    message: str = Field(default="Logout successful")


class LoginUserSchema(PreBasePydanticModel):
    email: str = Field(examples=["admin@admin.admin"])
    password: str = Field(examples=["qwer-qwer"])
