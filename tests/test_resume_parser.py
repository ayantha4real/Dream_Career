import pytest
from app.services.resume_parser import extract_text_from_pdf


def test_extract_text_from_nonexistent_file(caplog):
    """Ensure that extracting from a nonexistent PDF returns an empty string and logs an error."""
    result = extract_text_from_pdf('nonexistent_file.pdf')
    assert result == ""
    # Verify that an error was logged
    assert any('Failed to open PDF file' in record.message for record in caplog.records)
