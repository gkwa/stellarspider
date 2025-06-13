import json
import logging
import sys
import typing

import omegaconf


class OutputHandler:
    """Handles output formatting and writing following SRP."""

    def __init__(self, output_config: omegaconf.DictConfig):
        self.config = output_config
        self.logger = logging.getLogger(__name__)

    def write(self, data: typing.List[typing.Dict]) -> None:
        """Write data to stdout in configured format."""
        try:
            format_type = self.config.get("format", "json")

            if format_type == "json":
                self._write_json(data)
            else:
                raise ValueError(f"Unsupported output format: {format_type}")

        except Exception as e:
            self.logger.error(f"Error writing output: {e}")
            raise

    def _write_json(self, data: typing.List[typing.Dict]) -> None:
        """Write data as JSON to stdout."""
        indent = self.config.get("indent", 2)
        json.dump(data, sys.stdout, indent=indent)
        print()  # Add newline at end
