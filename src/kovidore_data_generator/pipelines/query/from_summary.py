from data_designer.essentials import (
    CategorySamplerParams,
    DataDesignerConfigBuilder,
    LLMTextColumnConfig,
    SamplerColumnConfig,
    SamplerType,
    SubcategorySamplerParams,
)

from kovidore_data_generator.utils import load_prompt
from kovidore_data_generator.pipelines.query.from_context import QUERY_TYPE_DEFINITIONS, QUERY_FORMAT_DEFINITIONS


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
            sampler_type=SamplerType.SUBCATEGORY,
            params=SubcategorySamplerParams(
                category="query_format",
                values={k: [v] for k, v in QUERY_FORMAT_DEFINITIONS.items()},
            ),
        )
    )

    # Add query_from_summary column
    config_builder.add_column(
        LLMTextColumnConfig(
            name="query_from_summary",
            model_alias=model_alias,
            prompt=load_prompt("query_from_summary"),
        ),
    )

    return config_builder
