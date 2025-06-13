import argparse
import importlib.metadata
import importlib.resources
import io
import logging
import sys
import typing

import omegaconf

from stellarspider.core.pipeline import FilterPipeline
from stellarspider.io.data_loader import DataLoader
from stellarspider.io.output_handler import OutputHandler


def setup_logging(verbose_count: int) -> None:
    """Configure logging based on verbosity level."""
    levels = [logging.WARNING, logging.INFO, logging.DEBUG]
    level = levels[min(verbose_count, len(levels) - 1)]

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,
    )


def load_config_file(
    package_path: str, filename: str
) -> typing.Optional[omegaconf.DictConfig]:
    """Load a single config file from package resources."""
    try:
        with importlib.resources.open_text(package_path, filename) as f:
            content = f.read()
            config_stream = io.StringIO(content)
            return omegaconf.OmegaConf.load(config_stream)
    except (FileNotFoundError, ModuleNotFoundError, ImportError) as e:
        logging.debug(f"Config file not found: {package_path}/{filename} - {e}")
        return None
    except Exception as e:
        logging.debug(f"Error loading config {package_path}/{filename}: {e}")
        return None


def load_configurations() -> (
    typing.Tuple[omegaconf.DictConfig, typing.Dict[str, omegaconf.DictConfig]]
):
    """Load all configuration files from package resources."""
    # Load main config
    main_config = load_config_file("stellarspider.conf", "config.yaml")
    if main_config is None:
        logging.debug("Using default main config")
        main_config = omegaconf.OmegaConf.create(
            {
                "input": None,
                "output": {"format": "json", "indent": 2},
                "verbose": 0,
                "version": False,
                "scoring": {"rule_weight": 0.7, "semantic_weight": 0.3},
            }
        )

    # Load category configs
    category_configs = {}
    for category in ["salmon", "peanuts"]:
        config = load_config_file("stellarspider.conf.category", f"{category}.yaml")
        if config:
            category_configs[category] = config
        else:
            logging.debug(f"Using fallback config for category: {category}")

    return main_config, category_configs


def create_fallback_salmon_config() -> omegaconf.DictConfig:
    """Create fallback salmon configuration."""
    return omegaconf.OmegaConf.create(
        {
            "category_name": "salmon",
            "filter_type": "salmon",
            "keywords": {
                "positive": [
                    "salmon",
                    "sockeye",
                    "pacific",
                    "alaska",
                    "coho",
                    "chinook",
                    "keta",
                ],
                "negative": [
                    "anchovies",
                    "atlantic",
                    "battered",
                    "biscuit",
                    "blackened",
                    "color added",
                    "sesame",
                    "bourbon",
                    "broccoli",
                    "burger",
                    "caesar salad",
                    "caviar",
                    "cedar plank",
                    "char",
                    "chicken",
                    "cod",
                    "cottage cheese",
                    "crusted",
                    "cubes",
                    "farm",
                    "farmed",
                    "garlic herb",
                    "grilled",
                    "guacamole",
                    "halibut",
                    "honey chipotle",
                    "juice",
                    "mahi mahi",
                    "marinated",
                    "mocktail",
                    "onion rings",
                    "peaches",
                    "plant based",
                    "pollock",
                    "previously frozen",
                    "rub",
                    "raised",
                    "sablefish",
                    "salad",
                    "sardines",
                    "seasoned",
                    "seasoning",
                    "shrimp",
                    "smoke",
                    "pacific cod",
                    "smoked",
                    "steak",
                    "stuffed",
                    "breaded",
                    "sweet potatoes",
                    "tilapia",
                    "tortillas",
                    "trout",
                    "tuna",
                    "vegan",
                ],
                "somewhat_negative": [
                    "canned",
                    "creations",
                    "servings",
                    "nuggets",
                    "poke bowl",
                    "pouch",
                    "teriyaki",
                ],
                "preferred": [
                    "fillet",
                    "fillets",
                    "frozen",
                    "fresh",
                    "wild",
                    "portion",
                    "portions",
                    "skinless",
                    "boneless",
                    "skin-on",
                    "never frozen",
                ],
            },
            "ocean_origins": {
                "atlantic": ["atlantic"],
                "pacific": ["pacific", "alaska", "alaskan"],
                "arctic": ["arctic"],
                "north_sea": ["north sea", "norwegian", "norway"],
                "other": ["canadian", "scottish", "faroese", "chilean", "tasmanian"],
            },
            "scoring": {
                "positive_multiplier": 3,
                "negative_multiplier": -10,
                "somewhat_negative_multiplier": -2,
                "preferred_multiplier": 2,
                "name_salmon_bonus": 4,
                "name_fillet_bonus": 3,
            },
            # Consumption preferences embedded in category config
            "consumption": {
                "frozen_storage": {
                    "frozen_bonus": 3,
                    "fresh_penalty": -5,
                    "negative_keywords": ["fresh", "never frozen"],
                },
                "immediate_use": {
                    "fresh_bonus": 2,
                    "frozen_penalty": 0,
                    "preferred_keywords": ["fresh", "never frozen"],
                },
            },
        }
    )


def create_fallback_peanuts_config() -> omegaconf.DictConfig:
    """Create fallback peanuts configuration."""
    return omegaconf.OmegaConf.create(
        {
            "category_name": "peanuts",
            "filter_type": "peanuts",
            "keywords": {
                "positive": [
                    "peanuts",
                    "peanut",
                    "groundnuts",
                    "spanish grade",
                    "valencia",
                    "runner",
                    "virginia",
                ],
                "negative": [
                    "peanut butter",
                    "chocolate",
                    "candy",
                    "bird feed",
                    "bird food",
                    "wildlife food",
                    "pet food",
                    "roasted",
                    "salted",
                    "seasoned",
                    "flavored",
                    "honey",
                    "caramel",
                    "cocktail mix",
                ],
                "somewhat_negative": ["blanched", "skinless", "shelled"],
                "preferred": [
                    "raw",
                    "uncooked",
                    "unsalted",
                    "organic",
                    "with skin",
                    "in shell",
                    "natural",
                ],
            },
            "scoring": {
                "positive_multiplier": 3,
                "negative_multiplier": -8,
                "somewhat_negative_multiplier": -1,
                "preferred_multiplier": 3,
                "name_peanut_bonus": 4,
                "raw_bonus": 5,
            },
            # Peanuts don't typically have consumption scenarios
            "consumption": {},
        }
    )


def create_final_config(
    main_config: omegaconf.DictConfig,
    category_configs: typing.Dict[str, omegaconf.DictConfig],
    args: argparse.Namespace,
) -> omegaconf.DictConfig:
    """Create final configuration by merging all sources."""
    # Start with main config
    final_config = omegaconf.OmegaConf.create(main_config)

    # Get category config (with fallback)
    if args.category in category_configs:
        category_config = category_configs[args.category]
        logging.debug(f"Using external config for category: {args.category}")
    else:
        logging.debug(f"Using fallback config for category: {args.category}")
        if args.category == "salmon":
            category_config = create_fallback_salmon_config()
        elif args.category == "peanuts":
            category_config = create_fallback_peanuts_config()
        else:
            raise ValueError(f"Unknown category: {args.category}")

    # Merge category config
    final_config = omegaconf.OmegaConf.merge(final_config, category_config)

    # Apply command line overrides
    final_config.verbose = args.verbose
    if args.input:
        final_config.input = args.input

    return final_config


def check_stdin_available() -> bool:
    """Check if stdin has data available without blocking."""
    import select
    import sys

    if sys.stdin.isatty():
        return False

    if hasattr(select, "select"):
        ready, _, _ = select.select([sys.stdin], [], [], 0)
        return bool(ready)

    return not sys.stdin.isatty()


def main() -> None:
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="NLP product filtering system",
        epilog="""
Examples:
  stellarspider --category salmon -i testdata/salmon_data.json
  stellarspider --category peanuts -i testdata/peanuts_data.json
  echo '[]' | stellarspider --category salmon
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {importlib.metadata.version('stellarspider')}",
    )

    parser.add_argument(
        "--category",
        default="salmon",
        choices=["salmon", "peanuts"],
        help="Product category to filter",
    )

    parser.add_argument(
        "--input", "-i", help="Input JSON file (use - or omit for stdin)"
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="count",
        default=0,
        help="Increase verbosity (use -v, -vv, -vvv)",
    )

    try:
        args = parser.parse_args()

        # Setup logging first
        setup_logging(args.verbose)
        logger = logging.getLogger(__name__)

        # Check for input source
        if not args.input and not check_stdin_available():
            print("Error: No input data provided.", file=sys.stderr)
            print("\nYou must provide input data either:", file=sys.stderr)
            print(
                "  1. Via file: stellarspider --category salmon -i testdata/salmon_data.json",
                file=sys.stderr,
            )
            print(
                "  2. Via stdin: echo '[]' | stellarspider --category salmon",
                file=sys.stderr,
            )
            print(
                "  3. Via stdin: cat testdata/salmon_data.json | stellarspider --category salmon",
                file=sys.stderr,
            )
            print("\nFor help: stellarspider --help", file=sys.stderr)
            sys.exit(1)

        # Load configurations
        main_config, category_configs = load_configurations()

        # Create final config
        final_config = create_final_config(main_config, category_configs, args)

        logger.info(f"Starting stellarspider with category: {args.category}")

        # Load input data
        data_loader = DataLoader()
        products = data_loader.load(final_config.get("input"))
        logger.info(f"Loaded {len(products)} products")

        # Create and run pipeline
        pipeline = FilterPipeline.from_config(final_config)
        filtered_products = pipeline.process(products)

        # Output results
        output_handler = OutputHandler(final_config.output)
        output_handler.write(filtered_products)

        logger.info(f"Processed {len(filtered_products)} products")

    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error in main: {e}")
        if args.verbose > 0:
            import traceback

            traceback.print_exc()
        sys.exit(1)
