import typing


class CombinedScoreCalculator:
    """Combines rule-based and semantic scores following SRP."""

    def __init__(self, rule_weight: float = 0.7, semantic_weight: float = 0.3):
        self.rule_weight = rule_weight
        self.semantic_weight = semantic_weight

    def calculate_final_score(
        self, products: typing.List[typing.Dict]
    ) -> typing.List[typing.Dict]:
        """Calculate weighted combined score."""
        for product in products:
            if "Scoring" not in product:
                product["Scoring"] = {}

            rule_score = product["Scoring"].get("rule_score", 0)
            semantic_score = product["Scoring"].get("semantic_score", 0)

            # Normalize rule score to 0-1 range
            normalized_rule = min(rule_score / 20, 1.0) if rule_score > 0 else 0

            final_score = (normalized_rule * self.rule_weight) + (
                semantic_score * self.semantic_weight
            )

            product["Scoring"]["final_score"] = round(final_score, 2)
            product["Scoring"]["weights"] = {
                "rule_weight": self.rule_weight,
                "semantic_weight": self.semantic_weight,
                "normalized_rule_score": normalized_rule,
            }

        return products
