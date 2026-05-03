"""
PDF Text Extractor
Uses PyMuPDF (fitz) as primary extractor with pypdf as fallback.
Handles both text-based and scanned PDFs.
"""

import os
from kivy.logger import Logger


class PDFExtractor:
    """Extracts clean text from PDF files for TTS conversion."""

    def __init__(self):
        self._fitz_available = self._check_fitz()
        self._pypdf_available = self._check_pypdf()

    def _check_fitz(self):
        try:
            import fitz
            return True
        except ImportError:
            return False

    def _check_pypdf(self):
        try:
            from pypdf import PdfReader
            return True
        except ImportError:
            return False

    def extract_text(self, pdf_path: str, progress_callback=None) -> str:
        """
        Extract text from a PDF file.

        Args:
            pdf_path: Full path to the PDF file
            progress_callback: Optional callable(percent: int, page: int, total: int)

        Returns:
            Extracted text as a single string
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        if self._fitz_available:
            return self._extract_with_fitz(pdf_path, progress_callback)
        elif self._pypdf_available:
            return self._extract_with_pypdf(pdf_path, progress_callback)
        else:
            raise ImportError(
                "No PDF library available. Install PyMuPDF: pip install pymupdf"
            )

    def _extract_with_fitz(self, pdf_path: str, progress_callback=None) -> str:
        import fitz

        Logger.info(f"PDFExtractor: Using PyMuPDF for {pdf_path}")
        doc = fitz.open(pdf_path)
        total = len(doc)
        text_parts = []

        for i, page in enumerate(doc):
            raw = page.get_text("text")
            cleaned = self._clean_text(raw)
            if cleaned.strip():
                text_parts.append(cleaned)

            if progress_callback:
                percent = int(((i + 1) / total) * 100)
                progress_callback(percent, i + 1, total)

        doc.close()
        full_text = "\n\n".join(text_parts)

        if not full_text.strip():
            Logger.warning("PDFExtractor: No text extracted — PDF may be scanned/image-based")
            raise ValueError(
                "This PDF appears to be scanned or image-based. "
                "Text extraction requires a text-based PDF."
            )

        return full_text

    def _extract_with_pypdf(self, pdf_path: str, progress_callback=None) -> str:
        from pypdf import PdfReader

        Logger.info(f"PDFExtractor: Using pypdf for {pdf_path}")
        reader = PdfReader(pdf_path)
        total = len(reader.pages)
        text_parts = []

        for i, page in enumerate(reader.pages):
            raw = page.extract_text() or ""
            cleaned = self._clean_text(raw)
            if cleaned.strip():
                text_parts.append(cleaned)

            if progress_callback:
                percent = int(((i + 1) / total) * 100)
                progress_callback(percent, i + 1, total)

        full_text = "\n\n".join(text_parts)

        if not full_text.strip():
            raise ValueError(
                "This PDF appears to be scanned or image-based. "
                "Text extraction requires a text-based PDF."
            )

        return full_text

    def _clean_text(self, text: str) -> str:
        """Remove junk characters and normalize whitespace."""
        import re
        # Remove non-printable except newlines/tabs
        text = re.sub(r"[^\x20-\x7E\n\t\u00A0-\uFFFF]", " ", text)
        # Collapse multiple spaces
        text = re.sub(r"[ \t]+", " ", text)
        # Collapse 3+ newlines into 2
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def get_page_count(self, pdf_path: str) -> int:
        """Return number of pages without extracting text."""
        if self._fitz_available:
            import fitz
            doc = fitz.open(pdf_path)
            n = len(doc)
            doc.close()
            return n
        elif self._pypdf_available:
            from pypdf import PdfReader
            return len(PdfReader(pdf_path).pages)
        return 0

    def get_metadata(self, pdf_path: str) -> dict:
        """Return PDF metadata (title, author, etc.)."""
        meta = {"title": "", "author": "", "pages": 0}
        if self._fitz_available:
            import fitz
            doc = fitz.open(pdf_path)
            m = doc.metadata
            meta["title"] = m.get("title", "") or os.path.basename(pdf_path)
            meta["author"] = m.get("author", "") or "Unknown"
            meta["pages"] = len(doc)
            doc.close()
        return meta
