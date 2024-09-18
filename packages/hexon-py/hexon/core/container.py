"""
Provides a set of classes and decorators to create a container, resolve its dependencies, and
manage the lifecycle of the injectable classes.
"""

import inspect
from abc import ABC
from dataclasses import dataclass, field
from typing import (
    Any,
    Dict,
    List,
    Literal,
    Optional,
    Tuple,
    Type,
    TypeVar,
    cast,
    final,
    get_type_hints,
)

from .logger import Logger
from .singleton import Singleton

ErrorCodes = Literal["NOT_FOUND", "INVALID_ELEMENT"]
"""A type that represents the error codes of the container."""


class ContainerError(Exception):
    """A custom exception to handle container errors."""

    code: ErrorCodes
    """The error code of the exception."""

    def __init__(self, message: str, code: ErrorCodes) -> None:
        super().__init__(message)
        self.code = code


T = TypeVar("T")
"""A type that represent any element type."""


class _Element(ABC):
    """A element is a base class for a Port, Adapter, or Container."""

    __element__: Literal["port", "adapter", "service", "container"]
    """The type of the element."""

    __token__: str
    """The token of the element used to identify in a container context."""

    __meta__: "_Meta"
    """The metadata of the element."""

    def __init__(self) -> None:
        if not hasattr(self, "__element__"):
            raise ContainerError("Property '__element__' not found.", "INVALID_ELEMENT")

        if not hasattr(self, "__token__"):
            raise ContainerError("Property '__token__' not found", "INVALID_ELEMENT")

        if not hasattr(self, "__meta__"):
            raise ContainerError("Property '__meta__' not found", "INVALID_ELEMENT")

    def __repr__(self) -> str:
        """Return the string representation of a injectable class."""
        return f"element={self.__element__}"


@dataclass
class _Resolution:
    """
    A container resolution is a dataclass that holds the instance of a provider or export,
    its dependencies, and the origin of the resolution.
    """

    token: str
    type: Literal["provider", "export"]
    instance: _Element
    deps: List[str]
    origin: Optional[str] = None
    from_cache: bool = False

    def __repr__(self) -> str:
        """Return the string representation of a container resolution."""
        parts = [
            f"<{self.instance}",
            f"type={self.type}",
            f"deps={self.deps}",
            f"origin={self.origin}",
            f"cache={self.from_cache}>",
        ]
        return ", ".join(parts)


@dataclass
class _Config:
    """The configuration for the container."""

    providers: List[Type[_Element]]
    """The list of providers."""

    exports: List[Type[_Element]]
    """The list of exports."""

    imports: List[Type["_Container"]] = field(default_factory=list)
    """The list of imported containers."""

    re_export: bool = False
    """If True, the container will re-export the exports of the imported containers."""


@dataclass
class _Meta:
    """
    Represents the metadata of a component (container or injectable). It relevant data
    to describe the component and their purpose.
    """

    name: str
    """The name of the component."""

    description: str
    """The description of the component."""

    version: str
    """The version of the component. Must follow the semantic versioning."""

    authors: List[str] = field(default_factory=list)
    """The authors of the component."""


@Singleton
class _Cache:
    """A singleton class to store containers and their resolutions."""

    _containers: Dict[str, "_Container"] = {}
    """A dictionary that stores all resolved containers."""

    def add(self, container: "_Container") -> None:
        """Add a container to the cache usign his token."""
        self._containers[container.__token__] = container

    def get(self, container: Type[T]):
        """Return the container for the given token (if exists)."""
        if not issubclass(container, _Container):
            raise ContainerError("The element must be a Container.", "INVALID_ELEMENT")

        return self.get_by_token(container.__token__)

    def try_get(self, container: Type[T]):
        if not issubclass(container, _Container):
            raise ContainerError("The element must be a Container.", "INVALID_ELEMENT")

        cache_container = self.get_by_token(container.__token__)

        if cache_container:
            return cache_container

        raise ContainerError(f"Container with token {container.__token__} not found", "NOT_FOUND")

    def get_by_token(self, token: str) -> Optional["_Container"]:
        """Return the container for the given token (if exists)."""
        try:
            return self._containers[token]
        except KeyError:
            return None

    def clear(self) -> None:
        """Clear the cache and the containers."""
        self._containers.clear()

    def get_provider(self, provider: Type[_Element]) -> Optional[_Resolution]:
        """Find a container in the cache by its class."""
        for container in self._containers.values():
            if provider.__token__ in container.providers:
                return container.resolutions[provider.__token__]

        return None

    @classmethod
    def containers(cls) -> Dict[str, "_Container"]:
        """Return all cached containers."""
        return cls._containers


class _Container(_Element, ABC):
    """
    A container is a class that holds a set of providers, manages their dependencies, and
    resolves them when needed. Also, exports a set of classes that can be by other containers.
    """

    __config__: _Config
    """The configuration of the container."""

    _resolutions: Dict[str, _Resolution]
    """Contains all the providers and exports registered in the container."""

    _cache = _Cache()
    """Contains all the containers registered in the running application."""

    def __init__(self) -> None:
        """Register the container and resolve its dependencies."""

        # Check if the container has the required properties.
        if not self.__config__:
            raise AttributeError("The container must have a '__config__' property.")

        if not self.__meta__:
            raise AttributeError("The container must have a '__meta__' property.")

        # Set the container properties.
        self._imports = self.__config__.imports
        self._providers = self.__config__.providers
        self._exports = self.__config__.exports
        self._re_export = self.__config__.re_export

        # The resolutions must be empty at the beginning, to conflict with other containers.
        self._resolutions = {}

        # Resolving the imports, providers, and exports of the container.
        self._resolve_imports()
        self._make_resolution()

    def __repr__(self) -> str:
        """Return the string representation of a container."""
        providers_names = [provider.__name__ for provider in self._providers]
        exports_names = [export.__name__ for export in self._exports]
        return f"<Container: (providers={providers_names}, exports={exports_names})>"

    def _resolve_imports(self) -> None:
        """Resolve the imports of the container."""
        if self._imports:
            for container_class in self._imports:
                # Check if the container was already resolved and cached before.
                container = self._cache.get(container_class)

                # Otherwise, resolve the container and cache it.
                if not container:
                    container = container_class()
                    Logger.warning(f"Container '{container_class.__token__}' resolved!")
                    self._cache.add(container)
                else:
                    Logger.info(f"Container '{container_class.__token__}' resolved from cache!")

                # Re-exporting imported containers.
                for symbol, resolution in container.exports.items():
                    resolution.origin = container.__class__.__name__
                    self._resolutions[symbol] = resolution
                    self._resolutions[symbol].from_cache = True

                    if self.__config__.re_export and resolution.type == "export":
                        Logger.debug(
                            f"Re-exported '{symbol}' from '{container.__class__.__name__}'"
                        )

                    self._resolutions[symbol].type = "provider"

    def _make_resolution(self) -> None:
        """Resolve the providers and exports of the container."""

        # Checking if the container was already resolved and cached before.
        container = self._cache.get_by_token(self.__token__)
        if container:
            self._resolutions = container._resolutions
            Logger.info(f"'{self.__token__}' resolved from cache!")
            return

        # Otherwise, resolve the providers and exports of the container.
        providers = self._providers + self._exports
        for provider in providers:
            resolution = self._cache.get_provider(provider)
            token = provider.__token__

            if resolution:
                Logger.info(f"'{token}' resolved from cache!")
                self._resolutions[token] = resolution
                self._resolutions[token].from_cache = True  # Mark the resolution as cached.
                self._resolutions[token].type = (
                    "export"
                    if provider in self._exports and self.__config__.re_export
                    else "provider"
                )
                continue

            instance, deps = self._resolve(provider)
            Logger.debug(f"'{token}' resolved with this dependencies: {deps}")
            self._resolutions[token] = _Resolution(
                token=token,
                type="provider" if provider in self._providers else "export",
                instance=instance,
                deps=deps,
            )

        # Adding the container cache.
        self._cache.add(self)

    def _resolve(self, cls: Type[_Element]) -> Tuple[_Element, List[str]]:
        """Resolve the dependencies for the given injectable class."""
        constructor_params = get_type_hints(cls.__init__)
        init_args = {}
        deps: List[str] = []

        for param, param_type in constructor_params.items():
            if param == "return":
                continue
            dependency = self._get(param_type)
            deps.append(f"<{param}, {dependency.__class__.__name__}>")
            init_args[param] = dependency

        # Check if all abstract methods from base classes are implemented in the adapter.
        return cls(**init_args), deps

    def _get(self, cls: Type[_Element]) -> _Element:
        """Get the injectable instance from the list of providers or resolutions."""
        # Get the injectable instance from the list of providers.
        for provider in self._providers + self._exports:
            if issubclass(provider, cls):
                return provider()

        # Otherwise, get the injectable instance from the list of resolutions.
        if cls.__token__ in self._resolutions:
            return self._resolutions[cls.__token__].instance

        raise KeyError(f"Provider with {cls.__name__} not found")

    @final
    @property
    def resolutions(self):
        """Return the resolutions of the container."""
        return self._resolutions

    @final
    @property
    def exports(self):
        """Return the providers exported by the container."""
        return {
            symbol: resolution
            for symbol, resolution in self._resolutions.items()
            if resolution.type == "export"
        }

    @final
    @property
    def providers(self):
        """Return the providers of the container."""
        return {
            symbol: resolution
            for symbol, resolution in self._resolutions.items()
            if resolution.type == "provider"
        }

    @final
    def get(self, element: Type[T]):
        """Return the instance of the injectable class."""

        if not issubclass(element, _Element):
            raise TypeError("The element must be a subclass of 'Element'.")

        try:
            return cast(T, self._resolutions[element.__token__].instance)
        except KeyError:
            raise KeyError(f"Provider with {element.__name__} not found")


# ################################################################################################
# # Container Tools
# ################################################################################################


class ContainerTools:
    """
    A utility class to check analize container elements. A element is any class declarated in
    the scope of the container. It can be @Port, @Adapter or @Container.
    """

    @staticmethod
    def is_element_or_raise(element: Any) -> None:
        """
        Check if a class is a container element.

        :param element: The element to be checked.
        :raises AttributeError: If the element is not a container element.
        """

        if not inspect.isclass(element):
            raise AttributeError("The element must be a class.")

        if not hasattr(element, "__meta__"):
            raise AttributeError("The element must have a '__meta__' property.")

        if not hasattr(element, "__token__"):
            raise AttributeError("The element must have a '__token__' property.")

    @classmethod
    def is_abstract(cls, element: Any) -> bool:
        """Check if a class is an abstract class."""
        return all(
            (
                (inspect.isabstract(element) or issubclass(element, ABC)),
                len(cls.get_abstract_methods(element)) > 0,
            )
        )

    @classmethod
    def get_abstract_methods(cls, element: Any) -> List[str]:
        """Return the abstract methods of a class."""

        abstract_methods: List[str] = []
        for name, attr in inspect.getmembers(element, predicate=inspect.isfunction):
            if getattr(attr, "__isabstractmethod__", False):
                abstract_methods.append(name)

        return abstract_methods


# ################################################################################################
# # Decorators
# ################################################################################################

# Element subclass.
Element = _Element


E = TypeVar("E")


class Port:
    """
    A decorator to create a port class.

    A Port is an abstract class that defines a set of methods that must be implemented by an
    Adapter. The port class must be a subclass of 'Element'. Automatically, the port class is
    marked as final, preventing it from being subclassed. The port class is used to define the
    contract between the adapter and the service.
    """

    def __init__(
        self,
        name: str,
        description: str,
    ) -> None:
        self.meta = _Meta(name, description, "", [])

    def __call__(self, cls: Type[E]):
        if not issubclass(cls, _Element):
            raise TypeError("The element must be a subclass of 'Element'.")

        # Element internal data setup.
        cls.__element__ = "port"
        cls.__token__ = cls.__name__
        cls.__meta__ = self.meta

        return cast(Type[E], cls)


class Adapter:
    """
    A decorator to create an adapter class.

    An adapter is an implementation of a abstract injectable class. This decorator makes the
    class final, preventing it from being subclassed, and ensures that all abstract methods from
    base classes are implemented. Also it cannot be subclassed.
    """

    def __init__(self, port: Type[_Element]) -> None:
        if port.__element__ != "port":
            raise TypeError("The element must be a subclass of 'Port'.")

        self.port = port

    def __call__(self, cls: Type[_Element]):
        # Check if all abstract methods are implemented in the adapter.
        self._check_adapter(cls, self.port)

        @final
        class Adapter(cls):  # type: ignore
            pass

        # Element internal data setup.
        Adapter.__name__ = cls.__name__
        Adapter.__element__ = "adapter"
        Adapter.__token__ = self.port.__token__  # The token name must be the original.
        Adapter.__meta__ = self.port.__meta__  # Inherit the metadata from the port.

        return Adapter

    @final
    @staticmethod
    def _check_adapter(adapter: Type[_Element], port: Type[_Element]) -> None:
        """Check if all abstract methods are implemented in the adapter."""
        implemented_methods = {
            name: attr
            for name, attr in adapter.__dict__.items()
            if not getattr(attr, "__isabstractmethod__", False)
        }

        for base_class in adapter.__bases__ + (port,):
            for name, attr in base_class.__dict__.items():
                if getattr(attr, "__isabstractmethod__", False):
                    if name not in implemented_methods:
                        raise NotImplementedError(
                            f"Method '{base_class.__name__}.{name}' is not implemented."
                        )


class Service:
    """
    A decorator to create a service class.

    A service is a class that provides a set of functionalities to the application. It can be
    a database connection, a logger, or a HTTP client. The service class must be a subclass of
    'Element' and must be final. Commonly, the service uses providers using the inversion of
    control principle, which means that the service does not create its dependencies, but it
    receives them from the container context by dependency injection.
    """

    def __init__(
        self,
        name: str,
        description: str,
        version: str,
        authors: List[str] = [],
    ) -> None:
        self.meta = _Meta(name, description, version, authors)

    def __call__(self, cls: Type[E]):
        if not issubclass(cls, _Element):
            raise TypeError("The element must be a subclass of 'Element'.")

        @final
        class Service(cls):  # type: ignore
            pass

        # Element internal data setup.
        Service.__element__ = "service"
        Service.__token__ = cls.__name__
        Service.__meta__ = self.meta

        return cast(Type[E], Service)


class Container:
    """
    A decorator to create a container class.

    A container is a class that holds a set of providers, manages their dependencies, and resolves
    them when needed. Also, exports a set of classes that can be by other containers. Containers
    can import other containers to re-use their providers and exports. All containers has its own
    cache to store the resolutions and avoid conflicts with other containers.
    """

    def __init__(
        self,
        name: str,
        description: str,
        version: str,
        authors: List[str] = [],
        providers: List[Type[_Element]] = [],
        exports: List[Type[_Element]] = [],
        imports: List[Type[_Element]] = [],
        re_export: bool = False,
    ) -> None:

        # Checking if imports are valid (must containers).
        for imp in imports:
            if not issubclass(imp, _Container):
                raise TypeError("The element must be a subclass of 'Container'.")

        self.config = _Config(providers, exports, cast(List[Type[_Container]], imports), re_export)
        self.meta = _Meta(name, description, version, authors)

    def __call__(self, cls: Type[E]):

        @final
        class Container(_Container, cls):  # type: ignore
            pass

        # Element internal data setup.
        Container.__name__ = cls.__name__
        Container.__element__ = "container"
        Container.__token__ = Container.__name__
        Container.__config__ = self.config
        Container.__meta__ = self.meta

        return Container
