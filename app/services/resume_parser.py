import logging
import os

import fitz


logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path):
    if not pdf_path or not os.path.exists(pdf_path):

        logger.error(
            "Failed to open PDF file: file does not exist (%s)",
            pdf_path
        )

        return ""

    text_parts = []

    try:

        doc = fitz.open(pdf_path)

    except Exception as exc:

        logger.error(
            "Failed to open PDF file (%s): %s",
            pdf_path,
            exc
        )

        return ""

    try:

        for page in doc:

            page_text = page.get_text("text")

            if page_text.strip():
                text_parts.append(page_text)

            try:
                tables = page.find_tables()

                for table in tables.tables:
                    table_data = table.extract()

                    for row in table_data:
                        row_text = " | ".join(
                            str(cell).strip()
                            if cell is not None
                            else ""
                            for cell in row
                        )

                        if row_text.strip():
                            text_parts.append(row_text)

            except Exception:
                pass

    finally:

        doc.close()

    return "\n".join(text_parts)
