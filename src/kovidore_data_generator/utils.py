from pathlib import Path

from data_designer.essentials import DataDesigner, DataDesignerConfigBuilder, ModelProvider
from data_designer.interface.results import DatasetCreationResults
import pandas as pd


def load_dataframe(file_path: Path | str) -> pd.DataFrame:
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".parquet":
        return pd.read_parquet(path)
    elif suffix == ".csv":
        return pd.read_csv(path)
    elif suffix == ".json":
        return pd.read_json(path)
    elif suffix == ".jsonl":
        return pd.read_json(path, lines=True)
    else:
        raise ValueError(f"Unsupported file format: {suffix}. Supported formats: .parquet, .csv, .json, .jsonl")


def create_dataset_from_seed(
    config_builder: DataDesignerConfigBuilder,
    model_providers: list[ModelProvider],
    seed_dataframe: pd.DataFrame,
    seed_file_path: Path | str,
    num_records: int,
    artifact_path: Path | str | None = None,
    dataset_name: str | None = None,
) -> DatasetCreationResults:
    data_designer = DataDesigner(artifact_path=artifact_path, model_providers=model_providers)

    seed_dataset_reference = data_designer.make_seed_reference_from_dataframe(
        dataframe=seed_dataframe,
        file_path=seed_file_path,
    )
    config_builder.with_seed_dataset(seed_dataset_reference)
    preview = data_designer.preview(config_builder, num_records=1)
    preview.display_sample_record()

    results = data_designer.create(config_builder, num_records=num_records, dataset_name=dataset_name)

    return results
