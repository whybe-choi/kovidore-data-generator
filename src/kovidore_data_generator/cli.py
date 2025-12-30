import argparse
import logging

from kovidore_data_generator.pipelines.run_pipeline import run_pipeline, PIPELINES
from kovidore_data_generator.config import ALL_SUBSETS

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model_alias",
        type=str,
        default="upstage-solar-pro2",
        help="Model alias to use for the pipeline",
    )
    parser.add_argument(
        "--subsets",
        nargs="*",
        default=ALL_SUBSETS,
        help=f"Subsets to run (default: all subsets). Available subsets: {', '.join(ALL_SUBSETS)}",
    )
    parser.add_argument(
        "--task",
        type=str,
        default="single_section_summary",
        choices=list(PIPELINES.keys()),
        help=f"Task to run (default: single_section_summary). Available tasks: {', '.join(PIPELINES.keys())}",
    )
    parser.add_argument(
        "--seed_file",
        type=str,
        default="exploded_corpus.parquet",
        help="Path to the seed dataset file (overrides subset default)",
    )
    parser.add_argument(
        "--num_records",
        type=int,
        default=None,
        help="Number of records to generate for the dataset",
    )
    parser.add_argument(
        "--list_subsets",
        action="store_true",
        help="List available subsets and exit",
    )
    parser.add_argument(
        "--list_tasks",
        action="store_true",
        help="List available tasks and exit",
    )
    args = parser.parse_args()

    if args.list_subsets:
        logger.info("Available subsets:")
        for subset in ALL_SUBSETS:
            logger.info(f"  - {subset}")
        return

    if args.list_tasks:
        logger.info("Available tasks:")
        for task in list(PIPELINES.keys()):
            logger.info(f"  - {task}")
        return

    run_pipeline(args)


if __name__ == "__main__":
    main()
