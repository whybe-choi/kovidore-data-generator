import argparse
import logging
from pathlib import Path
from pyexpat import model

from datasets import Dataset, Features, Image, Value
from tqdm import tqdm

from kovidore_data_generator.parser import UpstageDocumentParser
from kovidore_data_generator.config import ALL_SUBSETS

logger = logging.getLogger(__name__)


def main(args):
    # You can replace UpstageDocumentParser with any other parser you have implemented
    parser = UpstageDocumentParser()

    data_dir = Path(__file__).parent / "data"

    for subset_name in args.subsets:
        subset_dir = data_dir / subset_name
        pdfs_dir = subset_dir / "pdfs"
        images_dir = subset_dir / "images"

        if not pdfs_dir.exists():
            logger.warning(f"No pdfs directory found in {subset_name}")
            continue

        pdf_files = list(pdfs_dir.glob("*.pdf"))
        if not pdf_files:
            logger.warning(f"No PDF files found in {pdfs_dir}")
            continue

        logger.info(f"Processing subset: {subset_name} ({len(pdf_files)} PDF files)")

        data = []
        corpus_id = 0
        for pdf_file in pdf_files:
            doc_id = pdf_file.stem

            try:
                parser.convert_pdf_to_image(
                    pdf_path=str(pdf_file),
                    output_folder=str(images_dir),
                )

                image_files = sorted(
                    images_dir.glob(f"{doc_id}_*.png"),
                    key=lambda x: int(x.name.split("_")[-1].replace(".png", "")),
                )

                for image_file in tqdm(image_files, desc=f"Parsing images"):
                    page_number = int(image_file.name.split("_")[-1].replace(".png", ""))
                    try:
                        result = parser.parse_document(str(image_file))
                        markdown = result.get("content", "")
                        elements = result.get("elements", "")
                    except Exception as e:
                        logger.error(f"Error parsing {image_file}: {e}")
                        markdown = ""
                        elements = ""

                    data.append(
                        {
                            "corpus_id": corpus_id,
                            "image": str(image_file),
                            "doc_id": doc_id,
                            "markdown": markdown,
                            "elements": elements,
                            "page_number_in_doc": page_number,
                        }
                    )
                    corpus_id += 1

            except Exception as e:
                logger.error(f"Error converting {pdf_file}: {e}")

        if data:
            corpus_path = subset_dir / "corpus" / "data.parquet"

            features = Features(
                {
                    "corpus_id": Value("int64"),
                    "image": Image(),
                    "doc_id": Value("string"),
                    "markdown": Value("string"),
                    "elements": Value("string"),
                    "page_number_in_doc": Value("int64"),
                }
            )

            dataset = Dataset.from_list(data, features=features)
            dataset.to_parquet(corpus_path)
            logger.info(f"Saved parquet to {corpus_path} ({len(data)} rows)")

    logger.info("All subsets completed!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--subsets",
        nargs="*",
        default=ALL_SUBSETS,
        help=f"Subsets to run (default: all subsets). Available subsets: {', '.join(ALL_SUBSETS)}",
    )
    args = parser.parse_args()

    main(args)
