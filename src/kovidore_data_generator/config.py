from dataclasses import dataclass, field
from pathlib import Path

from data_designer.essentials import (
    ChatCompletionInferenceParams,
    ModelProvider,
    ModelConfig,
)

ALL_SUBSETS = ["hr", "cybersecurity", "economic", "energy"]

upstage_provider = ModelProvider(
    name="upstage",
    endpoint="https://api.upstage.ai/v1",
    api_key="UPSTAGE_API_KEY",
)

openai_provider = ModelProvider(
    name="openai",
    endpoint="https://api.openai.com/v1",
    api_key="OPENAI_API_KEY",
)

model_configs = [
    ModelConfig(
        alias="upstage-solar-pro2",
        model="solar-pro2",
        provider="upstage",
        inference_parameters=ChatCompletionInferenceParams(
            max_tokens=4096,
            temperature=0.7,
            top_p=0.9,
            extra_body={"reasoning_effort": "high"},
        ),
    ),
    ModelConfig(
        alias="openai-gpt-5-mini",
        model="gpt-5-mini",
        provider="openai",
        inference_parameters=ChatCompletionInferenceParams(
            max_tokens=4096,
            temperature=0.7,
            top_p=0.9,
            extra_body={"reasoning_effort": "medium"},
        ),
    ),
]


@dataclass
class PathConfig:
    data_dir: Path = field(default_factory=lambda: Path("data"))

    def seed_dir(self, subset: str) -> Path:
        return self.data_dir / subset / "seed"

    def corpus_dir(self, subset: str) -> Path:
        return self.data_dir / subset / "corpus"

    def subset_dir(self, subset: str) -> Path:
        return self.data_dir / subset

    def pipeline_output_dir(self, subset: str, task: str) -> Path:
        return self.data_dir / subset / task / "parquet-files"

    def seed_path(self, subset: str, task: str) -> Path:
        return self.seed_dir(subset) / f"seed_for_{task}.parquet"


path_config = PathConfig()


def get_input_path(task: str, subset: str) -> Path:
    paths = {
        "single_section_summary": path_config.corpus_dir(subset),
        "cross_section_summary": path_config.pipeline_output_dir(subset, "single_section_summary"),
        "query_from_context": path_config.corpus_dir(subset),
        "query_from_summary": path_config.pipeline_output_dir(subset, "cross_section_summary"),
        "filter_query_from_context": path_config.pipeline_output_dir(subset, "query_from_context"),
        "filter_query_from_summary": path_config.pipeline_output_dir(subset, "query_from_summary"),
    }
    return paths[task]
