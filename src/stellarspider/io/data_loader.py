import json
import logging
import sys
import typing


class DataLoader:
    """Handles loading data from various sources following SRP."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def load(self, input_source: typing.Optional[str]) -> typing.List[typing.Dict]:
        """Load data from file or stdin."""
        try:
            if input_source is None or input_source == "-":
                self.logger.debug("Reading from stdin")
                data = json.load(sys.stdin)
            else:
                self.logger.debug(f"Reading from file: {input_source}")
                with open(input_source, "r", encoding="utf-8") as f:
                    data = json.load(f)

            if not isinstance(data, list):
                raise ValueError("Input data must be a JSON array")

            self.logger.info(f"Loaded {len(data)} products")
            return data

        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON format: {e}")
            raise
        except FileNotFoundError:
            self.logger.error(f"Could not find file {input_source}")
            raise
        except Exception as e:
            self.logger.error(f"Error loading input data: {e}")
            raise
