from typing import Any

import mongoengine

from erdantic.core import FieldInfo, FullyQualifiedName
from erdantic.exceptions import UnknownModelTypeError
from erdantic.plugins import register_plugin

from .fields import convert_mongoengine_field
from .utils import get_model_color_fn

MongoModel = type[mongoengine.document.Document] | type[mongoengine.document.EmbeddedDocument]


def is_mongoengine_model(obj: Any) -> bool:
    """Predicate function to determine if an object is a MongoDB model (not an instance).

    Args:
        obj (Any): The object to check.

    Returns:
        bool: True if the object is a MongoDB model, False otherwise.
    """
    return isinstance(obj, type) and (
        (issubclass(obj, mongoengine.EmbeddedDocument) or issubclass(obj, mongoengine.Document))
        and hasattr(obj, "_fields_ordered")
    )


def get_fields_from_mongo_model(model: MongoModel) -> list[FieldInfo]:
    """Given a MongoDB model, return a list of FieldInfo instances for each field in the model.

    Args:
        model (MongoDBModel): The MongoDB model to get fields from.

    Returns:
        List[FieldInfo]: List of FieldInfo instances for each field in the model
    """
    if not is_mongoengine_model(model):
        raise UnknownModelTypeError(model=model, available_plugins=["mongoengine"])

    field_infos: list[FieldInfo] = []

    for name in model._fields_ordered:
        field = model._fields.get(name)
        field_type, field_type_formatted_str = convert_mongoengine_field(field)
        field_info = FieldInfo.from_raw_type(
            model_full_name=FullyQualifiedName.from_object(model),
            name=f"{name}{'*' if field.required else ''}",
            raw_type=field_type,
            type_formatted=field_type_formatted_str,
        )
        field_infos.append(field_info)

    return field_infos


def get_mongo_parent_classname(model: MongoModel) -> type:
    """Get the parent class name for a given MongoDB model."""
    if issubclass(model, mongoengine.Document):
        return mongoengine.Document
    if issubclass(model, mongoengine.EmbeddedDocument):
        return mongoengine.EmbeddedDocument

    raise NotImplementedError()


register_plugin(
    key="mongoengine",
    predicate_fn=is_mongoengine_model,
    get_fields_fn=get_fields_from_mongo_model,
    get_model_color_fn=get_model_color_fn,
    get_parent_class_name_fn=get_mongo_parent_classname,
)
