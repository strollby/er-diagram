from functools import singledispatch
import typing
from typing import Union

from bson import ObjectId
import mongoengine
from mongoengine.base import BaseField, get_document

from .constants import HTMLTags
from .utils import get_field_class_name, get_mongoengine_plugin_document, mark_color, mark_required


@singledispatch
def convert_mongoengine_field(field: BaseField) -> tuple[type, str]:
    return mark_required(field=field, field_type=type(field)), get_field_class_name(field)


@convert_mongoengine_field.register(mongoengine.EnumField)
def convert_enum(field: mongoengine.EnumField) -> tuple[type, str]:
    return mark_required(
        field=field, field_type=field._enum_cls
    ), f"{get_field_class_name(field)}{HTMLTags.LT}{mark_color(field._enum_cls)}{HTMLTags.GT}"


@convert_mongoengine_field.register(mongoengine.ObjectIdField)
def convert_id(field: mongoengine.ObjectIdField) -> tuple[type, str]:
    return mark_required(field=field, field_type=ObjectId), get_field_class_name(field)


@convert_mongoengine_field.register(mongoengine.ListField)
def convert_list_field(field: mongoengine.ListField) -> tuple[type, str]:
    sub_type, sub_type_str = convert_mongoengine_field(field.field)
    return list[
        mark_required(field=field, field_type=sub_type)
    ], f"{get_field_class_name(field)}{HTMLTags.LT}{sub_type_str}{HTMLTags.GT}"


@convert_mongoengine_field.register(mongoengine.LazyReferenceField)
@convert_mongoengine_field.register(mongoengine.ReferenceField)
@convert_mongoengine_field.register(mongoengine.EmbeddedDocumentField)
def convert_reference_fields(
    field: Union[
        mongoengine.LazyReferenceField,
        mongoengine.ReferenceField,
        mongoengine.EmbeddedDocumentField,
    ],
) -> tuple[type, str]:
    if isinstance(field.document_type_obj, str):
        field.document_type_obj = get_document(field.document_type_obj)

    return (
        mark_required(field=field, field_type=field.document_type_obj),
        f"{get_field_class_name(field)}{HTMLTags.LT}{mark_color(field.document_type_obj)}{HTMLTags.GT}",
    )


@convert_mongoengine_field.register(mongoengine.GenericReferenceField)
@convert_mongoengine_field.register(mongoengine.GenericEmbeddedDocumentField)
def convert_generic_reference_fields(
    field: Union[mongoengine.GenericReferenceField, mongoengine.GenericEmbeddedDocumentField],
) -> tuple[type, str]:
    choice_types = [get_mongoengine_plugin_document(choice) for choice in field.choices]

    final_types = [*choice_types]
    if not field.required:
        final_types.append(None)

    choices_str = "<br/>| ".join([mark_color(choice_type) for choice_type in choice_types])
    return (
        typing.Union[*final_types],
        f"{get_field_class_name(field)}{HTMLTags.LT}{choices_str}{HTMLTags.GT}",
    )
