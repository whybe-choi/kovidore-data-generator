from data_designer.essentials import (
    DataDesignerConfigBuilder,
    LLMStructuredColumnConfig,
)
from pydantic import BaseModel, Field
from enum import Enum

from kovidore_data_generator.prompts import FALSE_NEGATIVES_FILTERING_PROMPT

class RelevanceScore(int, Enum):
    """
    Relevance score for query-document pairs based on VidoRe v3 scoring system.
    """
    IRRELEVANT = 0
    CRITICALLY_RELEVANT = 1
    FULLY_RELEVANT = 2


class FilterFalseNegativesOutput(BaseModel):
    reasoning: str = Field(
        description=(
            "A detailed reasoning explaining why each document image is assigned its relevance score. "
            "For each image, explain what information it contains (or lacks) relative to the query."
        )
    )
    relevance_scores: list[RelevanceScore] = Field(
        description=(
            "A list of relevance scores for each query-document image pair:\n"
            "- 2 (FULLY_RELEVANT): The page contains the complete answer to the query.\n"
            "- 1 (CRITICALLY_RELEVANT): The page contains facts or information required to answer the query, but additional information from other pages is needed.\n"
            "- 0 (IRRELEVANT): The page does not contain information relevant to the query."
        )
    )

def build_filter_false_negs_config(
    model_alias: str,
    model_configs: list,
) -> DataDesignerConfigBuilder:
    config_builder = DataDesignerConfigBuilder(model_configs=model_configs)

    config_builder.add_column(
        LLMStructuredColumnConfig(
            name="relevance_labels",
            model_alias=model_alias,
            prompt=FALSE_NEGATIVES_FILTERING_PROMPT,
            output_format=FilterFalseNegativesOutput,
        ),
    )

    return config_builder