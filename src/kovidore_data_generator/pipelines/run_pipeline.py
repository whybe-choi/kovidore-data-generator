import argparse
import logging
from pathlib import Path

from kovidore_data_generator.config import upstage_provider, openai_provider, model_configs
from kovidore_data_generator.pipelines import (
    build_single_section_summary_config,
    build_cross_section_summary_config,
    build_query_from_summary_config,
    build_query_from_context_config,
)
from kovidore_data_generator.utils import create_dataset_from_seed, load_dataframe

logger = logging.getLogger(__name__)

PIPELINES = {
    "single_section_summary": build_single_section_summary_config,
    "cross_section_summary": build_cross_section_summary_config,
    "query_from_summary": build_query_from_summary_config,
    "query_from_context": build_query_from_context_config,
}


def run_pipeline(args):
    for subset_name in args.subsets:
        logger.info(f"Running pipelines for subset: {subset_name}")

        subset_dir = Path(f"data/{subset_name}")
        seed_file_path = subset_dir / "seed" / args.seed_file

        if not seed_file_path.exists():
            logger.warning(f"Seed file {seed_file_path} does not exist. Skipping subset {subset_name}.")
            continue

        config_builder = PIPELINES[args.task](
            model_alias=args.model_alias,
            model_configs=model_configs,
        )
        seed_dataframe = load_dataframe(seed_file_path)

        if args.task == "single_section_summary":
            results = create_dataset_from_seed(
                config_builder=config_builder,
                model_providers=[upstage_provider, openai_provider],
                seed_dataframe=seed_dataframe,
                seed_file_path=seed_file_path,
                num_records=len(seed_dataframe),  # Generate single-page summaries for all seed records
                artifact_path=subset_dir,
                dataset_name=args.task,
            )
        else:
            results = create_dataset_from_seed(
                config_builder=config_builder,
                model_providers=[upstage_provider, openai_provider],
                seed_dataframe=seed_dataframe,
                seed_file_path=seed_file_path,
                num_records=len(seed_dataframe) if args.num_records is None else args.num_records,
                artifact_path=subset_dir,
                dataset_name=args.task,
            )

        results.load_analysis().to_report()
