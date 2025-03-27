import importlib.metadata
import logging
import sys
from typing import TYPE_CHECKING, Any, List, Optional, Protocol, Sequence, TypeVar

if sys.version_info >= (3, 10):
    from typing import TypeGuard
else:
    from typing_extensions import TypeGuard

from typenames import typenames

from erdantic.exceptions import PluginNotFoundError

if TYPE_CHECKING:
    from erdantic.core import FieldInfo

logger = logging.getLogger(__name__)

CORE_PLUGINS = ("pydantic", "attrs", "dataclasses", "enum", "mongoengine")

_ModelType = TypeVar("_ModelType", bound=type)
_ModelType_co = TypeVar("_ModelType_co", bound=type, covariant=True)
_ModelType_contra = TypeVar("_ModelType_contra", bound=type, contravariant=True)


def load_plugins():
    for plugin in CORE_PLUGINS:
        logger.debug("Loading plugin: %s", plugin)
        try:
            importlib.import_module(f"erdantic.plugins.{plugin}")
            logger.debug("Plugin successfully loaded: %s", plugin)
        except ModuleNotFoundError:
            logger.debug("Plugin dependencies not found. Skipping: %s", plugin)


class ModelPredicate(Protocol[_ModelType_co]):
    """Protocol class for a predicate function for a plugin."""

    def __call__(self, obj: Any) -> TypeGuard[_ModelType_co]: ...


class ModelFieldExtractor(Protocol[_ModelType_contra]):
    """Protocol class for a field extractor function for a plugin."""

    def __call__(self, model: _ModelType_contra) -> Sequence["FieldInfo"]: ...


class ModelParentClassNameExtractor(Protocol[_ModelType_contra]):
    """Protocol class for a parent class name extractor function for a plugin."""

    def __call__(self, model: _ModelType_contra) -> type: ...


class ModelColorExtractor(Protocol[_ModelType_contra]):
    """Protocol class for a color extractor of model function for a plugin."""

    def __call__(self, model: _ModelType_contra) -> Optional[str]: ...


_registry: dict[
    str,
    tuple[ModelPredicate[_ModelType], ModelFieldExtractor[_ModelType]],
    Optional[ModelParentClassNameExtractor[_ModelType]],
    Optional[ModelColorExtractor[_ModelType]],
] = {}


def register_plugin(
    key: str,
    predicate_fn: ModelPredicate[_ModelType],
    get_fields_fn: ModelFieldExtractor[_ModelType],
    get_parent_class_name_fn: Optional[ModelParentClassNameExtractor[_ModelType]] = None,
    get_model_color_fn: Optional[ModelColorExtractor[_ModelType]] = None,
):
    """Register a plugin for a specific model class type.

    Args:
        key (str): An identifier for this plugin.
        predicate_fn (ModelPredicate): A predicate function to determine if an object is a class
            of the model that is supported by this plugin.
        get_fields_fn (ModelFieldExtractor): A function to extract fields from a model class that
            is supported by this plugin.
        get_parent_class_name_fn (ModelParentClassNameExtractor): A function to extract parent
            class name.
        get_model_color_fn (ModelColorExtractor): A function to extract get model color.
    """
    logger.debug("Registering plugin '%s'", key)
    if key in _registry:
        logger.warning("Overwriting existing implementation for key '%s'", key)
    _registry[key] = (predicate_fn, get_fields_fn, get_parent_class_name_fn, get_model_color_fn)


def list_plugins() -> List[str]:
    """List the keys of all registered plugins."""
    return list(_registry.keys())


def get_predicate_fn(key: str) -> ModelPredicate:
    """Get the predicate function for a plugin by its key."""
    try:
        return _registry[key][0]
    except KeyError:
        raise PluginNotFoundError(key=key)


def get_field_extractor_fn(key: str) -> ModelFieldExtractor:
    """Get the field extractor function for a plugin by its key."""
    try:
        return _registry[key][1]
    except KeyError:
        raise PluginNotFoundError(key=key)


def get_parent_class_name_extractor_fn(key: str) -> ModelParentClassNameExtractor:
    """Get the parent class name extractor function for a plugin by its key."""
    try:
        return _registry[key][2]
    except KeyError:
        raise PluginNotFoundError(key=key)


def get_model_color_extractor_fn(key: str) -> ModelParentClassNameExtractor:
    """Get the model color extrator function for a plugin by its key."""
    try:
        return _registry[key][3]
    except KeyError:
        raise PluginNotFoundError(key=key)


def identify_field_extractor_fn(tp: type) -> Optional[ModelFieldExtractor]:
    """Identify the field extractor function for a model type.

    Args:
        tp (type): A type annotation.

    Returns:
        ModelFieldExtractor | None: The field extractor function for a known model type, or None if
            the model type is not recognized by any registered plugins.
    """
    for key, (predicate_fn, get_fields_fn, *_) in _registry.items():
        if predicate_fn(tp):
            logger.debug("Identified '%s' as a '%s' model.", typenames(tp), key)
            return get_fields_fn
    logger.debug("'%s' is not a known model type.", typenames(tp))
    return None


def identify_parent_class_name_extractor_fn(tp: type) -> Optional[ModelParentClassNameExtractor]:
    """Identify the class name extractor function for a model type.

    Args:
        tp (type): A type annotation.

    Returns:
        ModelParentClassNameExtractor | None: The class name extractor function
            type or None if the model type is not recognized by any registered plugins.
    """
    for key, (predicate_fn, _, get_class_name_fn, _) in _registry.items():
        if predicate_fn(tp):
            logger.debug("Identified '%s' as a '%s' model.", typenames(tp), key)
            return get_class_name_fn
    logger.debug("'%s' is not a known model type.", typenames(tp))
    return None


def identify_model_color_extractor_fn(tp: type) -> Optional[ModelColorExtractor]:
    """Identify the model color extrator function for a model type.

    Args:
        tp (type): A type annotation.

    Returns:
        ModelColorExtractor | None: The class name extractor function or None if
            the model type is not recognized by any registered plugins.
    """
    for key, (predicate_fn, _, _, get_model_color_fn) in _registry.items():
        if predicate_fn(tp):
            logger.debug("Identified '%s' as a '%s' model.", typenames(tp), key)
            return get_model_color_fn
    logger.debug("'%s' is not a known model type.", typenames(tp))
    return None
