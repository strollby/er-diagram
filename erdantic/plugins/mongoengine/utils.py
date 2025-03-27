import typing
from typing import Union

import mongoengine
from mongoengine.base import BaseField, get_document
from enum import Enum

from .constants import Colors


def get_mongoengine_plugin_document(
    name_or_doc: Union[str, type[mongoengine.Document], type[mongoengine.EmbeddedDocument]],
) -> type[mongoengine.Document] | type[mongoengine.EmbeddedDocument]:
    if isinstance(name_or_doc, str):
        return get_document(name_or_doc)
    return name_or_doc


def get_model_color_fn(obj: typing.Type) -> typing.Optional[str]:
    """Function to get the color of MongoDB model.

    Args:
        obj (Type): The object to get color of.

    Returns:
        str: color
    """
    if issubclass(obj, mongoengine.Document):
        return Colors.DOCUMENT
    if issubclass(obj, mongoengine.EmbeddedDocument):
        return Colors.EMBEDDED_DOC
    if issubclass(obj, Enum):
        return Colors.ENUM

    return None


def get_field_class_name(field: BaseField) -> str:
    return field.__class__.__name__


def mark_required(field: BaseField, field_type: type) -> type:
    if not field.required:
        return typing.Union[field_type, None]
    return field_type


def mark_color(obj: type) -> str:
    return f'<font color="{get_model_color_fn(obj)}">{obj.__name__}</font>'
