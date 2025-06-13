import abc
import typing


class ProductFilter(abc.ABC):
    """Abstract base class for product filters following SRP."""

    @abc.abstractmethod
    def filter_products(
        self, products: typing.List[typing.Dict]
    ) -> typing.List[typing.Dict]:
        """Filter and score products."""
        pass


class FilterBuilder(abc.ABC):
    """Abstract builder for creating filters following Builder pattern."""

    @abc.abstractmethod
    def build(self) -> ProductFilter:
        """Build the configured filter."""
        pass
