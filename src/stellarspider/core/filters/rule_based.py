import logging
import typing

import omegaconf

from stellarspider.core.filters.base import FilterBuilder, ProductFilter
from stellarspider.core.scoring.price_extractor import PriceExtractor


class RuleBasedFilter(ProductFilter):
    """Rule-based filter using keyword matching following SRP."""

    def __init__(
        self,
        keywords: typing.Dict[str, typing.List[str]],
        scoring_config: typing.Dict[str, typing.Any],
        consumption_config: typing.Optional[typing.Dict] = None,
        ocean_origins: typing.Optional[typing.Dict] = None,
    ):
        self.keywords = keywords
        self.scoring_config = scoring_config
        self.consumption_config = consumption_config or {}
        self.ocean_origins = ocean_origins or {}
        self.price_extractor = PriceExtractor()
        self.logger = logging.getLogger(__name__)

    def _extract_ocean_origin(
        self, product: typing.Dict
    ) -> typing.Tuple[typing.Optional[str], typing.List[str]]:
        """Extract ocean/region origin information."""
        name = product.get("Name", "").lower()
        text = product.get("CleanedText", "").lower()
        combined_text = f"{name} {text}"

        found_origins = []
        primary_origin = None

        for ocean_type, keywords in self.ocean_origins.items():
            for keyword in keywords:
                if keyword in combined_text:
                    found_origins.append(keyword)
                    if primary_origin is None:
                        primary_origin = ocean_type

        return primary_origin, found_origins

    def _calculate_relevance_score(
        self, product: typing.Dict
    ) -> typing.Tuple[float, str, typing.Dict]:
        """Calculate relevance score for a product."""
        name = product.get("Name", "").lower()
        text = product.get("CleanedText", "").lower()
        combined_text = f"{name} {text}"

        score = 0
        reasons = []
        score_breakdown = {}

        # Process keyword categories
        for category, keywords in self.keywords.items():
            found = [kw for kw in keywords if kw in combined_text]
            multiplier = self.scoring_config.get(f"{category}_multiplier", 1)
            category_score = len(found) * multiplier
            score += category_score

            score_breakdown[f"{category}_keywords"] = {
                "score": category_score,
                "keywords": found,
            }

            if found:
                reasons.append(f"{category} ({len(found)}): {found}")

        # Apply consumption-specific adjustments
        frozen_req = self.consumption_config.get("frozen_requirements", {})
        scoring_adj = self.consumption_config.get("scoring_adjustments", {})

        for req_kw in frozen_req.get("required_keywords", []):
            if req_kw in combined_text:
                bonus = scoring_adj.get("frozen_bonus", 0)
                score += bonus
                reasons.append(f"Frozen requirement met: +{bonus}")

        for neg_kw in frozen_req.get("negative_keywords", []):
            if neg_kw in combined_text:
                penalty = scoring_adj.get("fresh_penalty", 0)
                score += penalty
                reasons.append(f"Fresh penalty: {penalty}")

        # Category-specific bonuses
        self._apply_category_bonuses(product, name, score, reasons, score_breakdown)

        # Extract ocean origin if applicable
        if self.ocean_origins:
            ocean_origin, origin_keywords = self._extract_ocean_origin(product)
            score_breakdown["ocean_origin"] = {
                "primary_origin": ocean_origin,
                "found_keywords": origin_keywords,
            }
            if ocean_origin:
                reasons.append(f"Ocean origin: {ocean_origin}")

        return score, "; ".join(reasons), score_breakdown

    def _apply_category_bonuses(
        self,
        product: typing.Dict,
        name: str,
        score: float,
        reasons: typing.List[str],
        score_breakdown: typing.Dict,
    ) -> None:
        """Apply category-specific bonuses."""
        # This can be overridden by subclasses for category-specific logic
        pass

    def filter_products(
        self, products: typing.List[typing.Dict]
    ) -> typing.List[typing.Dict]:
        """Filter and rank products by relevance."""
        self.logger.debug(f"Processing {len(products)} products with rule-based filter")

        for product in products:
            score, reasoning, score_breakdown = self._calculate_relevance_score(product)
            price = self.price_extractor.extract_price(product.get("CleanedText", ""))
            price_per_oz = self.price_extractor.calculate_price_per_oz(product, price)

            # Initialize scoring object
            if "Scoring" not in product:
                product["Scoring"] = {}

            product["Scoring"]["rule_score"] = score
            product["Scoring"]["rule_reasoning"] = reasoning
            product["Scoring"]["rule_breakdown"] = score_breakdown
            product["Scoring"]["extracted_price"] = price
            product["Scoring"]["price_per_oz"] = price_per_oz

            # Update top-level fields
            product["PricePerOZ"] = price_per_oz

        return products


class SalmonRuleBasedFilter(RuleBasedFilter):
    """Salmon-specific rule-based filter."""

    def _apply_category_bonuses(
        self,
        product: typing.Dict,
        name: str,
        score: float,
        reasons: typing.List[str],
        score_breakdown: typing.Dict,
    ) -> None:
        """Apply salmon-specific bonuses."""
        salmon_bonus = 0
        if "salmon" in name:
            salmon_bonus = self.scoring_config.get("name_salmon_bonus", 0)
            score += salmon_bonus
            reasons.append("Salmon in product name")
        score_breakdown["salmon_in_name"] = {"score": salmon_bonus}

        fillet_bonus = 0
        if "fillet" in name:
            fillet_bonus = self.scoring_config.get("name_fillet_bonus", 0)
            score += fillet_bonus
            reasons.append("Fillet in product name")
        score_breakdown["fillet_in_name"] = {"score": fillet_bonus}


class PeanutsRuleBasedFilter(RuleBasedFilter):
    """Peanuts-specific rule-based filter."""

    def _apply_category_bonuses(
        self,
        product: typing.Dict,
        name: str,
        score: float,
        reasons: typing.List[str],
        score_breakdown: typing.Dict,
    ) -> None:
        """Apply peanuts-specific bonuses."""
        peanut_bonus = 0
        if "peanut" in name:
            peanut_bonus = self.scoring_config.get("name_peanut_bonus", 0)
            score += peanut_bonus
            reasons.append("Peanut in product name")
        score_breakdown["peanut_in_name"] = {"score": peanut_bonus}

        raw_bonus = 0
        if "raw" in name:
            raw_bonus = self.scoring_config.get("raw_bonus", 0)
            score += raw_bonus
            reasons.append("Raw in product name")
        score_breakdown["raw_in_name"] = {"score": raw_bonus}


class RuleBasedFilterBuilder(FilterBuilder):
    """Builder for rule-based filters following Builder pattern."""

    def __init__(self, config: omegaconf.DictConfig):
        self.config = config

    def build(self) -> ProductFilter:
        """Build the appropriate rule-based filter."""
        filter_type = self.config.get("filter_type", "generic")

        # Convert to regular Python objects
        if hasattr(self.config, "keywords"):
            keywords = omegaconf.OmegaConf.to_object(self.config.keywords)
        else:
            keywords = {}

        if hasattr(self.config, "scoring"):
            scoring_config = omegaconf.OmegaConf.to_object(self.config.scoring)
        else:
            scoring_config = {}

        # Handle frozen requirements and scoring adjustments
        frozen_requirements = {}
        scoring_adjustments = {}

        if hasattr(self.config, "frozen_requirements"):
            frozen_requirements = omegaconf.OmegaConf.to_object(
                self.config.frozen_requirements
            )
        if hasattr(self.config, "scoring_adjustments"):
            scoring_adjustments = omegaconf.OmegaConf.to_object(
                self.config.scoring_adjustments
            )

        # Create consumption config structure
        full_consumption_config = {
            "frozen_requirements": frozen_requirements,
            "scoring_adjustments": scoring_adjustments,
        }

        # Handle ocean origins (only for categories that have them)
        ocean_origins = {}
        if hasattr(self.config, "ocean_origins"):
            ocean_origins = omegaconf.OmegaConf.to_object(self.config.ocean_origins)

        if filter_type == "salmon":
            return SalmonRuleBasedFilter(
                keywords, scoring_config, full_consumption_config, ocean_origins
            )
        elif filter_type == "peanuts":
            return PeanutsRuleBasedFilter(
                keywords, scoring_config, full_consumption_config
            )
        else:
            return RuleBasedFilter(
                keywords, scoring_config, full_consumption_config, ocean_origins
            )
