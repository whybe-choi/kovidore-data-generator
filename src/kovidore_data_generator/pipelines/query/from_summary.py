from data_designer.essentials import (
    CategorySamplerParams,
    DataDesignerConfigBuilder,
    LLMStructuredColumnConfig,
    SamplerColumnConfig,
    SamplerType,
    SubcategorySamplerParams,
)
from pydantic import BaseModel, Field

from kovidore_data_generator.prompts import QUERY_FROM_SUMMARY_PROMPT
from kovidore_data_generator.pipelines.query.from_context import QUERY_TYPE_DEFINITIONS, QUERY_FORMAT_DEFINITIONS

class QueryFromSummaryGenerationOutput(BaseModel):
    reasoning: str = Field(
        description=(
            "Step-by-step reasoning explaining: "
            "(1) Which specific pieces of information from different page summaries are being connected, "
            "(2) Why answering this query requires synthesizing information from multiple pages, "
            "(3) What relationship/comparison/causation the query explores between the identified pieces."
        )
    )
    related_page_numbers: list[int] = Field(
        description=(
            "A list of actual page numbers from 'page_number_in_doc' that contain the information required to answer the query. "
            "Use the exact page numbers provided in the input, not indices."
        )
    )
    query: str = Field(
        description=(
            "The final search query in Korean. "
            "It must be answerable ONLY by synthesizing information from the specified pages. "
        )
    )


def build_query_from_summary_config(
    model_alias: str,
    model_configs: list,
) -> DataDesignerConfigBuilder:
    config_builder = DataDesignerConfigBuilder(model_configs=model_configs)

    # Add query_type column
    config_builder.add_column(
        SamplerColumnConfig(
            name="query_type",
            sampler_type=SamplerType.CATEGORY,
            params=CategorySamplerParams(
                values=list(QUERY_TYPE_DEFINITIONS.keys()),
            ),
        )
    )

    # Add query_type_definition column
    config_builder.add_column(
        SamplerColumnConfig(
            name="query_type_definition",
            drop=True,
            sampler_type=SamplerType.SUBCATEGORY,
            params=SubcategorySamplerParams(
                category="query_type",
                values={k: [v] for k, v in QUERY_TYPE_DEFINITIONS.items()},
            ),
        )
    )

    # Add query format column
    config_builder.add_column(
        SamplerColumnConfig(
            name="query_format",
            sampler_type=SamplerType.CATEGORY,
            params=CategorySamplerParams(values=list(QUERY_FORMAT_DEFINITIONS.keys())),
        )
    )

    # Add query format definition column
    config_builder.add_column(
        SamplerColumnConfig(
            name="query_format_definition",
            drop=True,
            sampler_type=SamplerType.SUBCATEGORY,
            params=SubcategorySamplerParams(
                category="query_format",
                values={k: [v] for k, v in QUERY_FORMAT_DEFINITIONS.items()},
            ),
        )
    )

    # Add query_from_summary column
    config_builder.add_column(
        LLMStructuredColumnConfig(
            name="query_from_summary",
            model_alias=model_alias,
            prompt=QUERY_FROM_SUMMARY_PROMPT,
            output_format=QueryFromSummaryGenerationOutput,
        ),
    )

    return config_builder
