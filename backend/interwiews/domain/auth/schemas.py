from pydantic import Field

from interwiews.common.schemas import PreBasePydanticModel


class LoginSuccessSchema(PreBasePydanticModel):
    message: str = Field(default="Login successful")


class LogoutSuccessSchema(PreBasePydanticModel):
    message: str = Field(default="Logout successful")


class LoginUserSchema(PreBasePydanticModel):
    email: str = Field(examples=["supervisor@supervisor.supervisor"])
    password: str = Field(examples=["qwer-qwer"])
