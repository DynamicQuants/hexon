import copy

import pytest

from hexon.core.immutable import Immutable, ImmutableStateError


class AImmutableClass(Immutable):
    value: str

    def __init__(self, value: str):
        super().__init__(value=value)


class TestImmutable:
    @pytest.fixture
    def obj(self):
        return AImmutableClass("test")

    def test_init_sets_attributes(self, obj: AImmutableClass):
        """Test that the __init__ method sets the attributes."""
        obj = AImmutableClass(value="test")
        assert obj.value == "test"

    def test_setattr_raises_error(self, obj: AImmutableClass):
        """Test that trying to set an attribute raises an ImmutableStateError."""

        with pytest.raises(ImmutableStateError, match="Cannot modify immutable object"):
            obj.value = "value"

    def test_delattr_raises_error(self, obj: AImmutableClass):
        """Test that trying to delete an attribute raises an ImmutableStateError."""
        with pytest.raises(
            ImmutableStateError, match="Cannot delete attribute from immutable object"
        ):
            del obj.value

    def test_copy_returns_self(self, obj: AImmutableClass):
        """Test that __copy__ returns the object itself."""
        obj_copy = copy.copy(obj)
        assert obj_copy is obj, "Copy should return the original object"

    def test_deepcopy_returns_self(self, obj: AImmutableClass):
        """Test that __deepcopy__ returns the object itself."""
        obj_deepcopy = copy.deepcopy(obj)
        assert obj_deepcopy is obj, "Deepcopy should return the original object"
