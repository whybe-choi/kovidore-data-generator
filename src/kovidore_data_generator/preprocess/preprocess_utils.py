import logging
import random

import numpy as np
import pandas as pd
from tqdm.auto import tqdm

from kovidore_data_generator.config import path_config


logger = logging.getLogger(__name__)


def preprocess_for_single_section_summary(
    df: pd.DataFrame,
    subset: str,
) -> pd.DataFrame:
    exploded_df = df.explode("elements", ignore_index=True)

    seed_path = path_config.seed_path(subset, "single_section_summary")
    seed_path.parent.mkdir(parents=True, exist_ok=True)
    exploded_df.to_parquet(seed_path, index=False)
    logger.info("Seed dataset for single_section_summary saved to %s.", seed_path)

    return exploded_df


def preprocess_for_cross_section_summary(
    df: pd.DataFrame,
    subset: str,
    target_count: int = 150,
    size_candidates: list[int] = [3, 5, 7],
) -> pd.DataFrame:
    df_sorted = df.sort_values(by=["doc_id", "page_number_in_doc"])

    result_rows = []

    grouped = df_sorted.groupby("doc_id")
    for doc_id, group in tqdm(grouped, desc="Generating Combinations"):
        total_rows = len(group)

        indices = group.index.to_numpy()
        target_columns = [col for col in group.columns if col != "doc_id"]

        for _ in range(target_count):
            k = random.choice(size_candidates)
            actual_k = min(k, total_rows)

            selected_indices = np.random.choice(indices, size=actual_k, replace=False)
            selected_indices.sort()

            temp = df_sorted.loc[selected_indices]
            row_data = {"doc_id": doc_id}

            for col in target_columns:
                row_data[col] = temp[col].tolist()

            result_rows.append(row_data)

    final_df = pd.DataFrame(result_rows)
    seed_path = path_config.seed_path(subset, "cross_section_summary")
    seed_path.parent.mkdir(parents=True, exist_ok=True)
    final_df.to_parquet(seed_path, index=False)
    logger.info("Seed dataset for cross_section_summary saved to %s.", seed_path)

    return final_df


def preprocess_for_query_from_context(
    df: pd.DataFrame,
    subset: str,
    target_window_sizes: list[int] = [5, 7],
) -> pd.DataFrame:
    dfs = []

    for w in target_window_sizes:
        temp_df = pd.DataFrame(
            {col: [df[col].iloc[i : i + w].tolist() for i in range(len(df) - w + 1)] for col in df.columns}
        )
        dfs.append(temp_df)

    final_df = pd.concat(dfs, ignore_index=True)
    seed_path = path_config.seed_path(subset, "query_from_context")
    seed_path.parent.mkdir(parents=True, exist_ok=True)
    final_df.to_parquet(seed_path, index=False)
    logger.info("Seed dataset for query_from_context saved to %s.", seed_path)

    return final_df


def preprocess_for_query_from_summary(
    df: pd.DataFrame,
    subset: str,
) -> pd.DataFrame:
    seed_path = path_config.seed_path(subset, "query_from_summary")
    seed_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(seed_path, index=False)
    logger.info("Seed dataset for query_from_summary saved to %s.", seed_path)

    return df


def preprocess_for_filter_query_from_context(
    df: pd.DataFrame,
    subset: str,
) -> pd.DataFrame:
    df = df.rename(columns={"query_from_context": "query"})

    seed_path = path_config.seed_path(subset, "filter_query_from_context")
    seed_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(seed_path, index=False)
    logger.info("Seed dataset for filter_query_from_context saved to %s.", seed_path)

    return df


def preprocess_for_filter_query_from_summary(
    df: pd.DataFrame,
    subset: str,
) -> pd.DataFrame:
    df = df.rename(columns={"query_from_summary": "query"})

    seed_path = path_config.seed_path(subset, "filter_query_from_summary")
    seed_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(seed_path, index=False)
    logger.info("Seed dataset for filter_query_from_summary saved to %s.", seed_path)

    return df
