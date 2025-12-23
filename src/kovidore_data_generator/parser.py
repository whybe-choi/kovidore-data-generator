import logging
import requests
import os

import fitz

logger = logging.getLogger(__name__)


class UpstageDocumentParser:
    def __init__(self, output_format: str = "markdown"):
        self.api_key = os.environ.get("UPSTAGE_API_KEY")
        if not self.api_key:
            raise ValueError("UPSTAGE_API_KEY environment variable not set")

        self.endpoint = "https://api.upstage.ai/v1/document-digitization"
        self.model = "document-parse-nightly"
        self.output_format = output_format

    def convert_pdf_to_image(self, pdf_path: str, output_folder: str):
        document = fitz.open(pdf_path)
        document_name = pdf_path.split("/")[-1].replace(".pdf", "")

        logger.info(f"Converting PDF {document_name} to images...")

        for page in document:
            pix = page.get_pixmap(dpi=300)
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            pix.save(f"{output_folder}/{document_name}_{page.number + 1}.png")

    def parse_document(self, file_path: str) -> dict:
        response = requests.post(
            self.endpoint,
            headers={"Authorization": f"Bearer {self.api_key}"},
            data={
                "ocr": "force",
                "model": self.model,
                "output_format": self.output_format,
                "mode": "enhanced",
            },
            files={"document": open(file_path, "rb")},
        )
        if response.status_code == 200:
            response_dict = response.json()
            content = response_dict["content"][self.output_format]
            elements = response_dict["elements"]
            return {"content": content, "elements": elements}
        else:
            raise ValueError(f"Unexpected status code {response.status_code}.")
