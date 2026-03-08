from fastapi import HTTPException


class UserNotAuthorizedException(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=401, detail="User is not authorized")


class UserRoleNotMatchedException(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=401, detail="User role is not matched")


class UserCredentialsException(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=401, detail="Incorrect email or password")


class NotAllowedIPException(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=403, detail="Permission denied")


class UserAlreadyExistsException(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=409, detail="User with this email already exists")


class InvalidTokenException(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=401, detail="Invalid token")


class UserNotActiveException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=403,
            detail="Account is not active",
        )


class UserNotAdminException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=403,
            detail="Permission denied. User not admin",
        )


class WrongFileFormat(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=406,
            detail="Неверный формат файла. Загрузите файл со следующим расширением: mp3, wav, m4a, jpeg, png, webp или mp4",
        )


class NoContent(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=404,
            detail="Not found item.",
        )


class NotFoundItem(Exception):
    pass


class WrongDocumentFormat(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=406,
            detail="Неверный формат файла. Загрузите файл со следующим расширением: doc, docx или pdf",
        )


class WrongImageFormat(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=406,
            detail="Неверный формат изображения. Загрузите изображение со следующим расширением: jpeg, png или webp",
        )


class ItemNotExist(Exception):
    pass


class InjectExeption(Exception):
    pass


class BrockenPathExeption(Exception):
    pass


class InvalidEmailExeption(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=422,
            detail="Invalid email",
        )


AUTH_EXEPTIONS: tuple = (
    UserNotAdminException,
    UserNotActiveException,
    UserNotAuthorizedException,
    InvalidTokenException,
)
"""Exeptions for auth.
UserNotAuthorizedException: 401
UserNotAdminException: 403
UserNotActiveException: 401
InvalidTokenException: 401
"""


def UnprocessableEntity(result_constrain: bool, detail: str) -> None:
    if not result_constrain:
        raise HTTPException(status_code=422, detail=detail)
