from stellarspider.core.filters.rule_based import RuleBasedFilter


class TestRuleBasedFilter:
    """Test suite for RuleBasedFilter following good testing practices."""

    def test_filter_with_positive_keywords(self):
        """Test filtering with positive keywords."""
        keywords = {
            "positive": ["salmon", "fillet"],
            "negative": ["canned"],
            "preferred": ["fresh"],
        }
        scoring_config = {
            "positive_multiplier": 3,
            "negative_multiplier": -10,
            "preferred_multiplier": 2,
        }

        filter_instance = RuleBasedFilter(keywords, scoring_config)

        products = [
            {
                "Name": "Fresh Salmon Fillet",
                "CleanedText": "Current price: $12.99 Fresh salmon fillet 1 lb",
            }
        ]

        result = filter_instance.filter_products(products)

        assert len(result) == 1
        assert result[0]["Scoring"]["rule_score"] > 0
        assert "salmon" in result[0]["Scoring"]["rule_reasoning"]

    def test_filter_with_negative_keywords(self):
        """Test filtering with negative keywords."""
        keywords = {
            "positive": ["salmon"],
            "negative": ["canned", "processed"],
            "preferred": [],
        }
        scoring_config = {
            "positive_multiplier": 3,
            "negative_multiplier": -10,
            "preferred_multiplier": 2,
        }

        filter_instance = RuleBasedFilter(keywords, scoring_config)

        products = [
            {
                "Name": "Canned Salmon",
                "CleanedText": "Current price: $3.99 Canned salmon 6 oz",
            }
        ]

        result = filter_instance.filter_products(products)

        assert len(result) == 1
        # Should have negative score due to "canned" keyword
        assert result[0]["Scoring"]["rule_score"] < 0

    def test_empty_products_list(self):
        """Test filter with empty products list."""
        keywords = {"positive": ["salmon"], "negative": [], "preferred": []}
        scoring_config = {"positive_multiplier": 3}

        filter_instance = RuleBasedFilter(keywords, scoring_config)
        result = filter_instance.filter_products([])

        assert result == []
