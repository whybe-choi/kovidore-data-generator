from data_designer.essentials import DataDesignerConfigBuilder, ModelConfig, LLMTextColumnConfig

from kovidore_data_generator.prompts import CROSS_SECTION_SUMMARY_PROMPT


def build_cross_section_summary_config(
    model_alias: str,
    model_configs: list[ModelConfig],
) -> DataDesignerConfigBuilder:
    config_builder = DataDesignerConfigBuilder(model_configs=model_configs)

    config_builder.add_column(
        LLMTextColumnConfig(
            name="cross_section_summary",
            model_alias=model_alias,
            prompt=CROSS_SECTION_SUMMARY_PROMPT,
        ),
    )

    return config_builder
