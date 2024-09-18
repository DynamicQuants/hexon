from typing import Any, Dict, NoReturn

from typing_extensions import Self


class ImmutableStateError(Exception):
    """Raised when we try to modify immutable object."""

    pass


class Immutable:  # XXX: This can be replaced with @dataclass(frozen=True) ?
    """
    Base class for immutable objects.

    This class is used to create immutable objects. It is a base class that can be inherited
    by other classes to make them immutable. It overrides the __setattr__ and __delattr__
    methods to raise an exception when trying to modify or delete an attribute. It also
    overrides the __copy__ and __deepcopy__ methods to return the object itself, since it
    is already immutable.
    """

    def __init__(self, **attributes: Any) -> None:
        """Extracts attributes from kwargs and sets them as object attributes."""
        for attr_name, attr_value in attributes.items():
            super().__setattr__(attr_name, attr_value)

    def __copy__(self) -> Self:
        """Returns itself."""
        return self

    def __deepcopy__(self, memo: Dict[Any, Any]) -> Self:
        """Returns itself."""
        return self

    def __setattr__(self, attr_name: str, attr_value: Any) -> NoReturn:
        """Makes inner state immutable for modification."""
        raise ImmutableStateError("Cannot modify immutable object")

    def __delattr__(self, attr_name: str) -> NoReturn:
        """Makes inner state immutable for deletion."""
        raise ImmutableStateError("Cannot delete attribute from immutable object")
