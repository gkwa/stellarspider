from stellarspider.core.scoring.price_extractor import PriceExtractor


class TestPriceExtractor:
    """Test suite for PriceExtractor."""

    def test_extract_simple_price(self):
        """Test extracting simple dollar amount."""
        extractor = PriceExtractor()
        text = "Current price: $12.99 Fresh salmon"

        price = extractor.extract_price(text)

        assert price == 12.99

    def test_extract_price_with_spaces(self):
        """Test extracting price with spaces."""
        extractor = PriceExtractor()
        text = "Current price: $ 12 . 99 Fresh salmon"

        price = extractor.extract_price(text)

        assert price == 12.99

    def test_extract_no_price(self):
        """Test when no price is found."""
        extractor = PriceExtractor()
        text = "Fresh salmon fillet"

        price = extractor.extract_price(text)

        assert price is None

    def test_calculate_price_per_oz_direct(self):
        """Test calculating price per oz when directly stated."""
        extractor = PriceExtractor()
        product = {"Name": "Salmon", "CleanedText": "Price $12.99 ($0.81/ounce)"}

        price_per_oz = extractor.calculate_price_per_oz(product, 12.99)

        assert price_per_oz == 0.81

    def test_calculate_price_per_oz_from_weight(self):
        """Test calculating price per oz from weight."""
        extractor = PriceExtractor()
        product = {"Name": "Salmon 16 oz", "CleanedText": "Fresh salmon fillet"}

        price_per_oz = extractor.calculate_price_per_oz(product, 16.00)

        assert price_per_oz == 1.00
