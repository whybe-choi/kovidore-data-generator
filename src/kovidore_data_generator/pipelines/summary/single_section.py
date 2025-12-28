from data_designer.essentials import DataDesignerConfigBuilder, ModelConfig, LLMTextColumnConfig

from kovidore_data_generator.utils import load_prompt


def build_single_section_summary_config(
    model_alias: str,
    model_configs: list[ModelConfig],
) -> DataDesignerConfigBuilder:
    config_builder = DataDesignerConfigBuilder(model_configs=model_configs)

    config_builder.add_column(
        LLMTextColumnConfig(
            name="single_section_summary",
            model_alias=model_alias,
            prompt=load_prompt("single_section_summary"),
        ),
    )

    return config_builder
