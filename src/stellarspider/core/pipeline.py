import logging
import typing

import omegaconf

from stellarspider.core.filters.base import ProductFilter
from stellarspider.core.filters.rule_based import RuleBasedFilterBuilder
from stellarspider.core.filters.semantic import SemanticFilterBuilder
from stellarspider.core.scoring.combined_scorer import CombinedScoreCalculator


class FilterPipeline:
    """Pipeline that applies multiple filters in sequence using DIP."""

    def __init__(
        self,
        filters: typing.List[ProductFilter],
        score_calculator: CombinedScoreCalculator,
    ):
        self.filters = filters
        self.score_calculator = score_calculator
        self.logger = logging.getLogger(__name__)

    def process(self, products: typing.List[typing.Dict]) -> typing.List[typing.Dict]:
        """Apply all filters in sequence and calculate final scores."""
        self.logger.info(f"Processing {len(products)} products through pipeline")

        current_products = products

        # Apply filters
        for i, filter_instance in enumerate(self.filters):
            self.logger.debug(f"Applying filter {i + 1}/{len(self.filters)}")
            current_products = filter_instance.filter_products(current_products)

        # Calculate final scores
        final_products = self.score_calculator.calculate_final_score(current_products)

        # Sort by final score descending
        final_products.sort(
            key=lambda x: x.get("Scoring", {}).get("final_score", 0), reverse=True
        )

        self.logger.info("Pipeline processing complete")
        return final_products

    @classmethod
    def from_config(cls, config: omegaconf.DictConfig) -> "FilterPipeline":
        """Create pipeline from configuration using dependency injection."""
        filters = []

        # Build rule-based filter
        rule_builder = RuleBasedFilterBuilder(config)
        filters.append(rule_builder.build())

        # Build semantic filter
        semantic_builder = SemanticFilterBuilder(config)
        filters.append(semantic_builder.build())

        # Create score calculator
        scoring_config = config.get("scoring", {})
        score_calculator = CombinedScoreCalculator(
            rule_weight=scoring_config.get("rule_weight", 0.7),
            semantic_weight=scoring_config.get("semantic_weight", 0.3),
        )

        return cls(filters, score_calculator)
