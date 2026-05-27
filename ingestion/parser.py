"""
ingestion/parser.py
-------------------
Parses raw documents into clean plain text.
Supports PDF, Markdown, plain text, and HTML files.

This is the first step of the ingestion pipeline:
Raw file → Clean text string
"""

from pathlib import Path
from loguru import logger 
import pymupdf 
import re 


def parse_file(file_path: str | Path) -> str:
    """
    Parse a single file into clean plain text.

    Args:
        file_path: Path to the document file.

    Returns:
        Clean plain text string.

    Raises:
        ValueError: If the file type is not supported.
        FileNotFoundError: If the file does not exist.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    logger.info(f"Parsing file: {path.name}")

    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return _parse_pdf(path)
    elif suffix in (".md", ".txt"):
        return _parse_text(path)
    elif suffix == ".html":
        return _parse_html(path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}. Supported: .pdf, .md, .txt, .html")
    

def parse_directory(dir_path: str | Path) -> list[dict]:
    """
    Parse all supported documents in a directory.

    Args:
        dir_path: Path to the directory containing documents.

    Returns:
        List of dicts with keys: 'filename', 'content', 'file_type'
    """
    dir_path = Path(dir_path)

    if not dir_path.exists():
        raise FileNotFoundError(f"Directory not found: {dir_path}")
    
    supported_extensions = {".pdf", ".md", ".txt", ".html"}
    files = [f for f in dir_path.rglob("*") if f.suffix.lower() in supported_extensions]

    if not files:
        logger.warning(f"No supported files found in {dir_path}")
        return []

    logger.info(f"Found {len(files)} files to parse in {dir_path}")

    parsed_docs = []
    for file in files:
        try:
            content = parse_file(file)
            if content.strip():  # skip empty files
                parsed_docs.append({
                    "filename": file.name,
                    "filepath": str(file),
                    "content": content,
                    "file_type": file.suffix.lower(),
                })
                logger.success(f"Parsed: {file.name} ({len(content)} characters)")
        except Exception as e:
            # Log the error but continue parsing other files
            logger.error(f"Failed to parse {file.name}: {e}")

    logger.info(f"Successfully parsed {len(parsed_docs)}/{len(files)} files")
    return parsed_docs

# Helper methods 

def _parse_pdf(path: Path) -> str:
    """Extract text from a PDF file using PyMuPDF."""
    doc = pymupdf.open(path)
    text_parts = []

    for page_num, page in enumerate(doc, start=1):
        text = page.get_text()
        if text.strip():
            text_parts.append(text)

    doc.close()
    return _clean_text("\n".join(text_parts))


def _parse_text(path: Path) -> str:
    """Read plain text or markdown file."""
    return _clean_text(path.read_text(encoding="utf-8"))


def _parse_html(path: Path) -> str:
    """Extract text from HTML, stripping all tags."""
    from bs4 import BeautifulSoup
    html = path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    # Remove script and style elements
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    return _clean_text(soup.get_text(separator="\n"))


def _clean_text(text: str) -> str:
    """
    Clean raw extracted text.
    - Collapse multiple blank lines into one
    - Strip leading/trailing whitespace
    - Remove non-printable characters
    """
    # Remove non-printable characters except newlines and tabs
    text = re.sub(r'[^\x09\x0A\x20-\x7E\u00A0-\uFFFF]', '', text)
    # Collapse 3+ newlines into 2
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Strip leading/trailing whitespace
    return text.strip()