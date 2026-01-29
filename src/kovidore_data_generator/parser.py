import logging
import os
from abc import ABC, abstractmethod
from pathlib import Path

import fitz
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class BaseDocumentParser(ABC):
    @abstractmethod
    def parse_document(self, file_path: str | Path) -> dict:
        pass

    def convert_pdf_to_image(self, pdf_path: str | Path, output_folder: str | Path):
        document = fitz.open(pdf_path)
        document_name = Path(pdf_path).stem
        output_folder = Path(output_folder)
        output_folder.mkdir(parents=True, exist_ok=True)

        logger.info(f"Converting PDF {document_name} to images...")

        for page in document:
            pix = page.get_pixmap(dpi=300)
            image_path = output_folder / f"{document_name}_{page.number + 1}.png"
            pix.save(str(image_path))


class UpstageDocumentParser(BaseDocumentParser):
    ENDPOINT = "https://api.upstage.ai/v1/document-digitization"
    DEFAULT_MODEL = "document-parse-260128"

    def __init__(self, output_format: str = "markdown"):
        self.api_key = os.environ.get("UPSTAGE_API_KEY")
        if not self.api_key:
            raise ValueError("UPSTAGE_API_KEY environment variable not set")

        self.endpoint = self.ENDPOINT
        self.model = self.DEFAULT_MODEL
        self.output_format = output_format

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        before_sleep=lambda retry_state: logger.warning(
            f"Retry attempt {retry_state.attempt_number} for {retry_state.args[1]}: {retry_state.outcome.exception()}"
        ),
    )
    def parse_document(self, file_path: str | Path) -> dict:
        with open(file_path, "rb") as file:
            response = requests.post(
                self.endpoint,
                headers={"Authorization": f"Bearer {self.api_key}"},
                data={
                    "ocr": "force",
                    "model": self.model,
                    "output_format": self.output_format,
                    "mode": "enhanced",
                },
                files={"document": file},
            )

        if response.status_code != 200:
            raise ValueError(f"Unexpected status code {response.status_code}: {response.text}")

        response_dict = response.json()
        return {
            "content": response_dict["content"][self.output_format],
            "elements": response_dict["elements"],
        }
