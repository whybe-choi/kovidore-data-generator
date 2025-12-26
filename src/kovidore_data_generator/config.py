from data_designer.essentials import (
    ChatCompletionInferenceParams,
    ModelProvider,
    ModelConfig,
)

ALL_TASKS = ["hr", "cybersecurity", "financial", "energy"]

upstage_provider = ModelProvider(
    name="upstage",
    endpoint="https://api.upstage.ai/v1",
    api_key="UPSTAGE_API_KEY",
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
    )
]
