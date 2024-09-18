from abc import abstractmethod

import pytest

from hexon.core.container import _Cache  # type: ignore
from hexon.core.container import _Container  # type: ignore
from hexon.core.container import _Meta  # type: ignore
from hexon.core.container import (
    Adapter,
    Container,
    ContainerError,
    ContainerTools,
    Element,
    Port,
    Service,
)

# ################################################################################################
# # Elements
# ################################################################################################


class NotElement:
    pass


class EmptyElement(Element):
    pass


class ElementWithElementTag(Element):
    __element__ = "port"


class ElementWithElementTagAndToken(Element):
    __element__ = "port"
    __token__ = "ElementWithElementTagAndToken"


class ElementWithElementTagAndTokenAndMeta(Element):
    __element__ = "port"
    __token__ = "ElementWithElementTagAndTokenAndMeta"
    __meta__ = _Meta(
        name="ElementWithElementTagAndTokenAndMeta",
        description="ElementWithElementTagAndTokenAndMeta",
        version="0.1.0",
    )


# ################################################################################################
# # Substractor
# ################################################################################################


@Port(
    name="substractor",
    description="Substractor port that defines the substract method",
)
class SubstractorPort(Element):
    @abstractmethod
    def substract(self, a: float, b: float) -> float: ...


@Adapter(SubstractorPort)
class SubstractorAdapter(Element):
    def substract(self, a: float, b: float) -> float:
        return a - b


@Service(
    name="calculator",
    description="Calculator service that uses the substractor port",
    version="0.1.0",
)
class SubstractorService(Element):
    def __init__(self, substractor: SubstractorPort):
        self.substract = substractor.substract

    def make_substraction(self, a: float, b: float) -> float:
        return self.substract(a, b)


@Container(
    name="SubstractorContainer",
    description="A container to substract two numbers",
    version="0.1.0",
    providers=[SubstractorAdapter],
    exports=[SubstractorService],
)
class SubstractorContainer(Element):
    pass


# ################################################################################################
# # Adder
# ################################################################################################


@Port(
    name="adder",
    description="Adder port that defines the add method",
)
class AdderPort(Element):
    @abstractmethod
    def add(self, a: float, b: float) -> float: ...


@Adapter(AdderPort)
class AdderAdapter(Element):
    def add(self, a: float, b: float) -> float:
        return a + b


@Service(
    name="AdderService",
    description="Calculator service that uses the adder port",
    version="0.1.0",
)
class AdderService(Element):
    def __init__(self, adder: AdderPort):
        self.add = adder.add

    def make_addition(self, a: float, b: float) -> float:
        return self.add(a, b)


@Container(
    name="AdderContainer",
    description="A container to add two numbers",
    version="0.1.0",
    providers=[AdderAdapter],
    exports=[AdderService],
)
class AdderContainer(Element):
    pass


# ################################################################################################
# # Multiplier
# ################################################################################################


@Port(
    name="multiplier",
    description="Multiplier port that defines the multiply method",
)
class MultiplierPort(Element):
    @abstractmethod
    def multiply(self, a: float, b: float) -> float: ...


@Adapter(MultiplierPort)
class MultiplierAdapter(Element):
    def multiply(self, a: float, b: float) -> float:
        return a * b


@Service(
    name="MultiplierService",
    description="Calculator service that uses the multiplier port",
    version="0.1.0",
)
class MultiplierService(Element):
    def __init__(self, multiplier: MultiplierPort):
        self.multiply = multiplier.multiply

    def make_multiplication(self, a: float, b: float) -> float:
        return self.multiply(a, b)


@Container(
    name="MultiplierContainer",
    description="A container to multiply two numbers",
    version="0.1.0",
    providers=[MultiplierAdapter],
    exports=[MultiplierService],
)
class MultiplierContainer(Element):
    pass


# ################################################################################################
# # Divider
# ################################################################################################


@Port(
    name="divider",
    description="Divider port that defines the divide method",
)
class DividerPort(Element):
    @abstractmethod
    def divide(self, a: float, b: float) -> float: ...


@Adapter(DividerPort)
class DividerAdapter(Element):
    def divide(self, a: float, b: float) -> float:
        return a / b


@Service(
    name="DividerService",
    description="Calculator service that uses the divider port",
    version="0.1.0",
)
class DividerService(Element):
    def __init__(self, divider: DividerPort):
        self.divide = divider.divide

    def make_division(self, a: float, b: float) -> float:
        return self.divide(a, b)


@Container(
    name="DividerContainer",
    description="A container to divide two numbers",
    version="0.1.0",
    providers=[DividerAdapter],
    exports=[DividerService],
)
class DividerContainer(Element):
    pass


# ################################################################################################
# # Calculator
# ################################################################################################


@Service(
    name="CalculatorService",
    description="Calculator service that uses the four basic operations",
    version="0.1.0",
)
class CalculatorService(Element):
    def __init__(
        self,
        adder: AdderPort,
        substractor: SubstractorPort,
        multiplier: MultiplierPort,
        divider: DividerPort,
    ):
        self._add = adder.add
        self._substract = substractor.substract
        self._multiply = multiplier.multiply
        self._divide = divider.divide

    def calculate(self, operation: str) -> float:
        elements = operation.split(" ")

        if len(elements) != 3:
            raise ValueError("Invalid operation")

        a = float(elements[0])
        b = float(elements[2])
        operator = elements[1]

        match = {
            "+": self._add,
            "-": self._substract,
            "*": self._multiply,
            "/": self._divide,
        }

        if operator not in match:
            raise ValueError("Invalid operator")

        return match[operator](a, b)


@Service(
    name="CalculatorService",
    description="Calculator service that uses the four basic operations",
    version="0.1.0",
)
class CalculatorServiceFromServices(Element):
    def __init__(
        self,
        adder: AdderService,
        substractor: SubstractorService,
        multiplier: MultiplierService,
        divider: DividerService,
    ):
        self._add = adder.add
        self._substract = substractor.substract
        self._multiply = multiplier.multiply
        self._divide = divider.divide

    def calculate(self, operation: str) -> float:
        elements = operation.split(" ")

        if len(elements) != 3:
            raise ValueError("Invalid operation")

        a = float(elements[0])
        b = float(elements[2])
        operator = elements[1]

        match = {
            "+": self._add,
            "-": self._substract,
            "*": self._multiply,
            "/": self._divide,
        }

        if operator not in match:
            raise ValueError("Invalid operator")

        return match[operator](a, b)


@Container(
    name="CalculatorContainer",
    description="A container to calculate operations",
    version="0.1.0",
    providers=[AdderAdapter, SubstractorAdapter, MultiplierAdapter, DividerAdapter],
    exports=[CalculatorService],
)
class CalculatorWithMultipleProvidersContainer:
    pass


@Container(
    name="CalculatorContainer",
    description="A container to calculate operations",
    version="0.1.0",
    imports=[AdderContainer, SubstractorContainer, MultiplierContainer, DividerContainer],
    exports=[CalculatorServiceFromServices],
)
class CalculatorWithImportsContainer:
    pass


# ################################################################################################
# # Tests
# ################################################################################################


class TestElement:
    """Test the element and its restrictions."""

    def test_element_restrictions(self):
        with pytest.raises(ContainerError) as error:
            EmptyElement()

        assert error.value.code == "INVALID_ELEMENT"

        with pytest.raises(ContainerError) as error:
            ElementWithElementTag()

        assert error.value.code == "INVALID_ELEMENT"

        with pytest.raises(ContainerError) as error:
            ElementWithElementTagAndToken()

        assert error.value.code == "INVALID_ELEMENT"

        # Checking
        valid_element = ElementWithElementTagAndTokenAndMeta()
        assert valid_element.__element__ == "port"
        assert valid_element.__token__ == "ElementWithElementTagAndTokenAndMeta"
        assert valid_element.__meta__.name == "ElementWithElementTagAndTokenAndMeta"
        assert valid_element.__meta__.description == "ElementWithElementTagAndTokenAndMeta"
        assert valid_element.__meta__.version == "0.1.0"

    def test_tools(self):
        assert ContainerTools.is_abstract(SubstractorPort) is True
        assert ContainerTools.is_abstract(SubstractorAdapter) is False
        assert ContainerTools.get_abstract_methods(SubstractorPort) == ["substract"]
        assert ContainerTools.get_abstract_methods(SubstractorAdapter) == []

        with pytest.raises(AttributeError):
            ContainerTools.is_element_or_raise(NotElement)


class TestContainer:
    """Test the container and its elements."""

    def test_basic_container(self):
        """A simple container means that it has only providers and exports."""
        substractor = SubstractorContainer()
        assert isinstance(substractor, _Container)
        assert len(substractor.resolutions) == 2
        assert len(substractor.providers) == 1
        assert len(substractor.exports) == 1

        substractor_adapter = substractor.get(SubstractorPort)
        assert substractor_adapter.substract(5, 3) == 2

        substractor_service = substractor.get(SubstractorService)
        assert substractor_service.make_substraction(5, 3) == 2

    def test_multiple_providers_container(self):
        """Multiprovider container."""

        calculator = CalculatorWithMultipleProvidersContainer()
        assert isinstance(calculator, _Container)

        assert len(calculator.resolutions) == 5
        assert len(calculator.providers) == 4
        assert len(calculator.exports) == 1

        calculator_service = calculator.get(CalculatorService)
        assert calculator_service.calculate("5 + 3") == 8
        assert calculator_service.calculate("5 - 3") == 2
        assert calculator_service.calculate("5 * 3") == 15
        assert calculator_service.calculate("6 / 3") == 2

    def test_composed_containers(self):
        """A composed container means that it has nested containers (imports)."""

        calculator = CalculatorWithImportsContainer()
        assert isinstance(calculator, _Container)

        assert len(calculator.resolutions) == 5
        assert len(calculator.providers) == 4
        assert len(calculator.exports) == 1

        calculator_service = calculator.get(CalculatorServiceFromServices)
        assert calculator_service.calculate("5 + 3") == 8
        assert calculator_service.calculate("5 - 3") == 2
        assert calculator_service.calculate("5 * 3") == 15
        assert calculator_service.calculate("6 / 3") == 2


class TestCache:
    """Test the cache that stores the containers."""

    def test_cache_get(self):
        assert len(_Cache().containers()) == 6

        # Should be the same as the previous test.
        calculator = _Cache().try_get(CalculatorWithImportsContainer)

        assert len(calculator.resolutions) == 5
        assert len(calculator.providers) == 4
        assert len(calculator.exports) == 1

        with pytest.raises(ContainerError) as error:
            _Cache().try_get(SubstractorAdapter)

        assert error.value.code == "INVALID_ELEMENT"

        with pytest.raises(ContainerError) as error:
            _Cache().get(SubstractorAdapter)

        assert error.value.code == "INVALID_ELEMENT"

    def test_cache_clear(self):
        _Cache().clear()
        assert len(_Cache().containers()) == 0

        with pytest.raises(ContainerError) as error:
            _Cache().try_get(CalculatorWithImportsContainer)

        assert error.value.code == "NOT_FOUND"
