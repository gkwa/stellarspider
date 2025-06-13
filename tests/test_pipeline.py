from stellarspider.core.filters.rule_based import RuleBasedFilter
from stellarspider.core.pipeline import FilterPipeline
from stellarspider.core.scoring.combined_scorer import CombinedScoreCalculator


class TestFilterPipeline:
    """Test suite for FilterPipeline."""

    def test_pipeline_processes_products(self):
        """Test that pipeline processes products through filters."""
        # Create simple filter
        keywords = {"positive": ["salmon"], "negative": [], "preferred": []}
        scoring_config = {"positive_multiplier": 3}
        rule_filter = RuleBasedFilter(keywords, scoring_config)

        # Create score calculator
        score_calc = CombinedScoreCalculator()

        # Create pipeline
        pipeline = FilterPipeline([rule_filter], score_calc)

        products = [
            {"Name": "Salmon Fillet", "CleanedText": "Fresh salmon fillet $12.99"}
        ]

        result = pipeline.process(products)

        assert len(result) == 1
        assert "Scoring" in result[0]
        assert "final_score" in result[0]["Scoring"]

    def test_pipeline_sorts_by_score(self):
        """Test that pipeline sorts products by final score."""
        keywords = {"positive": ["salmon"], "negative": [], "preferred": []}
        scoring_config = {"positive_multiplier": 3}
        rule_filter = RuleBasedFilter(keywords, scoring_config)

        score_calc = CombinedScoreCalculator()
        pipeline = FilterPipeline([rule_filter], score_calc)

        products = [
            {
                "Name": "Tuna",  # Lower score
                "CleanedText": "Fresh tuna $10.99",
            },
            {
                "Name": "Salmon Fillet",  # Higher score
                "CleanedText": "Fresh salmon fillet $12.99",
            },
        ]

        result = pipeline.process(products)

        assert len(result) == 2
        # First product should have higher score
        assert (
            result[0]["Scoring"]["final_score"] >= result[1]["Scoring"]["final_score"]
        )
