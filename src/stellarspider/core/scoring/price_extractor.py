import re
import typing


class PriceExtractor:
    """Handles price extraction and per-unit calculations following SRP."""

    def extract_price(self, text: str) -> typing.Optional[float]:
        """Extract price from product text."""
        price_patterns = [
            r"\$\s*(\d+\.\d{2})",  # $10.99
            r"\$\s*(\d+)\s*\.\s*(\d{2})",  # $10 . 99
            r"price:\s*\$\s*(\d+\.\d{2})",  # price: $10.99
            r"(\d+\.\d{2})\s*/\s*ea",  # 10.99 / ea
        ]

        for pattern in price_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                if isinstance(matches[0], tuple):
                    return float(f"{matches[0][0]}.{matches[0][1]}")
                else:
                    return float(matches[0])
        return None

    def calculate_price_per_oz(
        self, product: typing.Dict, price: typing.Optional[float]
    ) -> typing.Optional[float]:
        """Calculate price per ounce for comparison."""
        text = product.get("CleanedText", "").lower()
        name = product.get("Name", "").lower()
        combined = f"{name} {text}"

        # Direct price per ounce patterns
        price_per_oz_patterns = [
            r"\$\s*(\d+\.\d{2})/oz",
            r"\$\s*(\d+\.\d{2})\s*/\s*oz",
            r"\(\$\s*(\d+\.\d{2})/ounce\)",
            r"\(\$\s*(\d+\.\d{2})\s*/\s*ounce\)",
            r"(\d+\.\d{2})\s*/\s*oz",
            r"\$\s*(\d+\.\d{2})\s*/\s*oz",
        ]

        for pattern in price_per_oz_patterns:
            matches = re.findall(pattern, combined)
            if matches:
                return float(matches[0])

        # Price per pound patterns (convert to per ounce)
        price_per_lb_patterns = [
            r"\$(\d+\.\d{2})/lb",
            r"\$(\d+\.\d{2})\s*/\s*lb",
            r"\$\s*(\d+\.\d{2})\s*/\s*lb",
            r"\$\s*(\d+)\s*\.\s*(\d{2})\s*/\s*lb",
            r"(\d+\.\d{2})\s*/\s*lb",
            r"\$(\d+\.\d{2})\s*per\s*pound",
            r"price:\s*\$(\d+\.\d{2})\s*per\s*pound",
        ]

        for pattern in price_per_lb_patterns:
            matches = re.findall(pattern, combined)
            if matches:
                if isinstance(matches[0], tuple):
                    price_per_lb = float(f"{matches[0][0]}.{matches[0][1]}")
                else:
                    price_per_lb = float(matches[0])
                return round(price_per_lb / 16, 2)

        # Calculate from base price and weight
        if not price:
            return None

        weight_patterns = [
            r"(\d+(?:\.\d+)?)\s*oz",
            r"(\d+(?:\.\d+)?)\s*ounce",
            r"(\d+(?:\.\d+)?)\s*lb",
            r"(\d+(?:\.\d+)?)\s*pound",
        ]

        for pattern in weight_patterns:
            matches = re.findall(pattern, combined)
            if matches:
                weight = float(matches[0])
                if "lb" in pattern or "pound" in pattern:
                    weight *= 16  # Convert pounds to ounces
                return round(price / weight, 2)

        return None
