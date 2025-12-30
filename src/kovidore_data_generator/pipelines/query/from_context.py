from data_designer.essentials import (
    CategorySamplerParams,
    DataDesignerConfigBuilder,
    LLMStructuredColumnConfig,
    SamplerColumnConfig,
    SamplerType,
    SubcategorySamplerParams,
)
from pydantic import BaseModel, Field

from kovidore_data_generator.prompts import QUERY_FROM_CONTEXT_PROMPT

QUERY_TYPE_DEFINITIONS = {
    "open-ended": "A query requiring synthesis and explanation of information. The answer must integrate multiple concepts into a coherent narrative rather than citing a single fact.",
    "compare-contrast": "A query requiring identification and articulation of similarities and/or differences between two or more entities, concepts, or topics.",
    "enumeration": "A query requesting a complete list of items that meet specific criteria.",
    "numerical": "A query expecting a numerical value, obtained either by direct extraction or calculation.",
    "boolean": "A query expecting a yes/no answer, potentially requiring reasoning over extracted information.",
    "extractive": "A query answerable by directly citing a specific fact or piece of information from the documents.",
    "multi-hop": "A query requiring information retrieval from multiple distinct sources or sections, which must then be combined to produce a complete answer.",
}

QUERY_FORMAT_DEFINITIONS = {
    "question": "A query presented in the form of a direct question, seeking specific information or clarification.",
    "instruction": "A query framed as a directive or command, requesting the model to perform a specific task or provide information in a particular manner.",
    "keyword": "A query consisting of noun phrases and keywords only, WITHOUT forming a complete sentence. No verbs, no question words, no sentence endings. Mimics how users type into search engines: fragmented, concise, noun-centric terms separated by spaces.",
}


class QueryFromContextGenerationOutput(BaseModel):
    reasoning: str = Field(
        description=(
            "Step-by-step reasoning explaining: "
            "(1) Which specific pieces of information from different page summaries are being connected, "
            "(2) Why answering this query requires synthesizing information from multiple pages, "
            "(3) What relationship/comparison/causation the query explores between the identified pieces."
        )
    )
    related_page_indices: list[int] = Field(
        description=(
            "A list of page indices (e.g., [0, 1, 2]) containing the information required to answer the query."
        )
    )
    query: str = Field(
        description=(
            "The final search query in Korean. "
            "It must be answerable ONLY by synthesizing information from the specified pages. "
        )
    )
    answer: str = Field(
        description=(
            "The answer to the query in Korean, based on synthesizing information from the specified pages. "
            "It should be a concise, factual response without additional explanations."
        )
    )


def build_query_from_context_config(
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

    # Add query_from_context column
    config_builder.add_column(
        LLMStructuredColumnConfig(
            name="query_from_context",
            model_alias=model_alias,
            prompt=QUERY_FROM_CONTEXT_PROMPT,
            output_format=QueryFromContextGenerationOutput,
        ),
    )

    return config_builder
