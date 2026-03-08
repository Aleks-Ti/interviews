from typing import Any

from pydantic import BaseModel


class PreBasePydanticModel(BaseModel):
    class Config:
        from_attributes = True


class MetaFormDataclass(type):
    def __new__(cls, name: str, bases: tuple, attrs: dict):
        validators = []
        for attr_name, attr_value in attrs.items():
            if callable(attr_value) and attr_name.startswith("super_validate_"):
                validators.append(attr_value)

        attrs["_validators"] = validators
        original_post_init = attrs.get("__post_init__", None)

        def new_post_init(self):
            if original_post_init:
                original_post_init(self)

            for validator in self._validators:
                validator(self)

        attrs["__post_init__"] = new_post_init

        return super().__new__(cls, name, bases, attrs)


class DataClassMixin(metaclass=MetaFormDataclass):
    def to_dict(self, exclude_none=False) -> dict[str, Any]:
        new_dict = {}
        if exclude_none:
            new_dict.update({key: value for key, value in self.__dict__.items() if value is not None})
            return new_dict
        new_dict.update(self.__dict__)
        return new_dict

    def to_dict_and_set_new_value(self, *attrs: tuple[str, str], exclude_none=False) -> dict:
        if exclude_none:
            new_dict = {attr[0]: attr[1] for attr in attrs if attr and attr[1] is not None}
            new_dict.update({key: value for key, value in self.__dict__.items() if value is not None})
        else:
            new_dict = {attr[0]: attr[1] for attr in attrs}
            new_dict.update(self.__dict__)

        return new_dict
