import logging
import os

import pandas as pd

from kovidore_data_generator.pipelines.run_pipeline import PIPELINES
from kovidore_data_generator.preprocess.preprocess_utils import (
    preprocess_for_single_section_summary,
    preprocess_for_cross_section_summary,
    preprocess_for_query_from_context,
    preprocess_for_query_from_summary,
)

PREPROCESS_MAP = {
    "single_section_summary": preprocess_for_single_section_summary,
    "cross_section_summary": preprocess_for_cross_section_summary,
    "query_from_context": preprocess_for_query_from_context,
    "query_from_summary": preprocess_for_query_from_summary,
}

INPUT_PATH_MAP = {
    "single_section_summary": "data/{subset}/corpus",
    "cross_section_summary": "data/{subset}/single_section_summary/parquet-files",
    "query_from_context": "data/{subset}/corpus",
    "query_from_summary": "data/{subset}/cross_section_summary/parquet-files",
}

logger = logging.getLogger(__name__)


def run_preprocess(args):
    for subset in args.subsets:
        logger.info(f"Subset: {subset}")
        logger.info("=" * 50)

        input_path = INPUT_PATH_MAP[args.task].format(subset=subset)
        logger.info(f"Input path: {input_path}")

        df = pd.read_parquet(input_path)

        if not os.path.exists(f"data/{subset}/seed"):
            os.makedirs(f"data/{subset}/seed")

        if args.task in PIPELINES:
            logger.info(f"Task: {args.task}")
            df = PREPROCESS_MAP[args.task](df=df, subset=subset)
            logger.info(f"Length after preprocessing: {len(df)}")
        else:
            raise ValueError(f"Unknown task: {args.task}")
