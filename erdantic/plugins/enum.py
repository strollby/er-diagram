from enum import Enum, IntEnum, ReprEnum, StrEnum
import typing
from typing import Any

from erdantic.core import FieldInfo, FullyQualifiedName
from erdantic.exceptions import UnknownModelTypeError
from erdantic.plugins import register_plugin

EnumModel = type[Enum]


def is_enum_model(obj: Any) -> bool:
    """Predicate function to determine if an object is an Enum model (not an instance).

    Args:
        obj (Any): The object to check.

    Returns:
        bool: True if the object is a Enum model, False otherwise.
    """
    return isinstance(obj, type) and (
        issubclass(obj, Enum) and obj not in (Enum, StrEnum, IntEnum, ReprEnum)
    )


def get_fields_from_enum_model(model: EnumModel) -> list[FieldInfo]:
    """Given an Enum model, return a list of FieldInfo instances for each field in the model.

    Args:
        model (EnumModel): The Enum model to get fields from.

    Returns:
        List[FieldInfo]: List of FieldInfo instances for each field in the model
    """
    if not is_enum_model(model):
        raise UnknownModelTypeError(model=model, available_plugins=["mongoengine"])

    field_infos: list[FieldInfo] = []

    for _enum in list(model):
        field_info = FieldInfo.from_raw_type(
            model_full_name=FullyQualifiedName.from_object(model),
            name=_enum.name,
            raw_type=type(_enum.value),
            type_formatted=_enum.value,
        )
        field_infos.append(field_info)

    return field_infos


def get_parent_classname_enum(model: EnumModel) -> type:
    """Get the parent class name for a given Enum model."""
    if issubclass(model, Enum):
        return Enum

    raise NotImplementedError()


def get_model_color_fn(obj: typing.Type) -> typing.Optional[str]:
    """Function to get the color of Enum model.

    Args:
        obj (Type): The object to get color of.

    Returns:
        str: color
    """
    if issubclass(obj, Enum):
        return "darkorange2"

    return None


register_plugin(
    key="enum",
    predicate_fn=is_enum_model,
    get_fields_fn=get_fields_from_enum_model,
    get_model_color_fn=get_model_color_fn,
    get_parent_class_name_fn=get_parent_classname_enum,
)
