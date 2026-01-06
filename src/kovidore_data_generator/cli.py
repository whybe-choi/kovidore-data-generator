import argparse
import logging

from kovidore_data_generator.config import ALL_SUBSETS
from kovidore_data_generator.pipelines.run_pipeline import run_pipeline, PIPELINES
from kovidore_data_generator.preprocess.run_preprocess import run_preprocess

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Synthetic Data Generation Pipeline for KoViDoRe Benchmark")
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

    subparsers = parser.add_subparsers(dest="command")

    # preprocess subcommand
    preprocess_parser = subparsers.add_parser("preprocess", help="Preprocess seed dataset for pipeline input")
    preprocess_parser.add_argument(
        "--subsets",
        nargs="*",
        default=ALL_SUBSETS,
        help=f"Subsets to preprocess. Available: {', '.join(ALL_SUBSETS)}",
    )
    preprocess_parser.add_argument(
        "--task",
        type=str,
        default="single_section_summary",
        choices=list(PIPELINES.keys()),
        help=f"Task to preprocess for. Available: {', '.join(PIPELINES.keys())}",
    )

    # pipeline subcommand
    pipeline_parser = subparsers.add_parser("pipeline", help="Run data generation pipeline")
    pipeline_parser.add_argument(
        "--model_alias",
        type=str,
        default="upstage-solar-pro2",
        help="Model alias to use for the pipeline",
    )
    pipeline_parser.add_argument(
        "--subsets",
        nargs="*",
        default=ALL_SUBSETS,
        help=f"Subsets to run. Available: {', '.join(ALL_SUBSETS)}",
    )
    pipeline_parser.add_argument(
        "--task",
        type=str,
        default="single_section_summary",
        choices=list(PIPELINES.keys()),
        help=f"Task to run. Available: {', '.join(PIPELINES.keys())}",
    )
    pipeline_parser.add_argument(
        "--num_records",
        type=int,
        default=None,
        help="Number of records to generate",
    )

    args = parser.parse_args()

    if args.list_subsets:
        print("Available subsets:")
        for subset in ALL_SUBSETS:
            print(f"  - {subset}")
        return

    if args.list_tasks:
        print("Available tasks:")
        for task in PIPELINES.keys():
            print(f"  - {task}")
        return

    if args.command is None:
        parser.print_help()
        return

    if args.command == "preprocess":
        run_preprocess(args)
    elif args.command == "pipeline":
        run_pipeline(args)


if __name__ == "__main__":
    main()
