import logging

import pandas as pd

from kovidore_data_generator.config import get_pipeline_input_path
from kovidore_data_generator.preprocess.preprocess_utils import (
    preprocess_for_single_section_summary,
    preprocess_for_cross_section_summary,
    preprocess_for_query_from_context,
    preprocess_for_query_from_summary,
    preprocess_for_filter_query_from_context,
    preprocess_for_filter_query_from_summary,
)


PREPROCESS_MAP = {
    "single_section_summary": preprocess_for_single_section_summary,
    "cross_section_summary": preprocess_for_cross_section_summary,
    "query_from_context": preprocess_for_query_from_context,
    "query_from_summary": preprocess_for_query_from_summary,
    "filter_query_from_context": preprocess_for_filter_query_from_context,
    "filter_query_from_summary": preprocess_for_filter_query_from_summary,
}

logger = logging.getLogger(__name__)


def run_preprocess(args):
    for subset in args.subsets:
        logger.info("=" * 100)
        logger.info(f"Subset: {subset}")
        logger.info("=" * 100)

        input_path = get_pipeline_input_path(args.task, subset)
        logger.info(f"Input path: {input_path}")

        df = pd.read_parquet(input_path)

        if args.task in PREPROCESS_MAP:
            logger.info(f"Task: {args.task}")
            df = PREPROCESS_MAP[args.task](df=df, subset=subset)
            logger.info(f"Length after preprocessing: {len(df)}")
            logger.info("=" * 100)
        else:
            raise ValueError(f"Unknown task: {args.task}")
