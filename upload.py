import argparse
import os
from datasets import Dataset, DatasetDict, Image
import pandas as pd


def main(args):
    data_dir = os.path.join(os.path.dirname(__file__), "data", args.subset_name)
    huggingface_id = args.huggingface_id
    repo_name = f"{huggingface_id}/kovidore-v2-{args.subset_name}-beir-test"
    print(repo_name)

    corpus_df = pd.read_csv(os.path.join(data_dir, "corpus.csv"))
    document_metadata_df = pd.read_csv(os.path.join(data_dir, "document_metadata.csv"))
    # queries_df = pd.read_csv(os.path.join(data_dir, "queries.csv"))
    # qrels_df = pd.read_csv(os.path.join(data_dir, "qrels.csv"))

    corpus_dataset = Dataset.from_pandas(corpus_df).cast_column("image", Image(decode=True))
    document_metadata_dataset = Dataset.from_pandas(document_metadata_df)
    # queries_dataset = Dataset.from_pandas(queries_df)
    # qrels_dataset = Dataset.from_pandas(qrels_df)

    configs = {
        "corpus": DatasetDict({"test": corpus_dataset}),
        "document_metadata": DatasetDict({"test": document_metadata_dataset}),
        # "queries": DatasetDict({"test": queries_dataset}),
        # "qrels": DatasetDict({"test": qrels_dataset}),
    }

    for config_name, dataset in configs.items():
        dataset.push_to_hub(
            repo_name,
            config_name=config_name,
            private=True,
            token=args.token,
            commit_message=f"Upload {config_name} config for KoViDoRe dataset in BEIR format",
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--huggingface_id", type=str, default="whybe-choi")
    parser.add_argument("--subset_name", type=str, default="hr")
    parser.add_argument("--token", type=str, required=True)
    args = parser.parse_args()
    main(args)
