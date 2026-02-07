"""LlamaCloud parsing pipeline for tweet images."""

from __future__ import annotations

import os
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx

from models import ParsedImageResult, ParseTier, TableResult


class LlamaCloudParseError(Exception):
    """Raised when parsing fails irrecoverably."""


@dataclass(frozen=True)
class ParseSettings:
    """Controls for image parsing mode."""

    tier: ParseTier
    enable_chart_parsing: bool = True


async def parse_image_from_url(
    image_url: str,
    api_key: str,
    settings: ParseSettings,
    client: httpx.AsyncClient | None = None,
) -> ParsedImageResult:
    """Download an image and parse it using LlamaCloud."""
    should_close = client is None
    http_client = client or httpx.AsyncClient(timeout=30.0)

    filename = _filename_from_url(image_url)
    try:
        response = await http_client.get(image_url)
        response.raise_for_status()
        return await parse_image_bytes(
            image_bytes=response.content,
            filename=filename,
            image_url=image_url,
            api_key=api_key,
            settings=settings,
        )
    except Exception as exc:
        return ParsedImageResult(
            image_url=image_url,
            filename=filename,
            success=False,
            error=str(exc),
        )
    finally:
        if should_close:
            await http_client.aclose()


async def parse_image_bytes(
    image_bytes: bytes,
    filename: str,
    image_url: str,
    api_key: str,
    settings: ParseSettings,
) -> ParsedImageResult:
    """Parse image bytes using AsyncLlamaCloud parse APIs."""
    if not api_key.startswith("llx-"):
        return ParsedImageResult(
            image_url=image_url,
            filename=filename,
            success=False,
            error="Invalid LlamaCloud API key format.",
        )

    try:
        from llama_cloud import AsyncLlamaCloud  # type: ignore
    except ImportError as exc:  # pragma: no cover - environment-specific guard
        raise LlamaCloudParseError(
            "Failed to import AsyncLlamaCloud from llama_cloud: "
            f"{exc}. Python executable: {sys.executable}. "
            "Install backend requirements in this same environment and restart the backend."
        ) from exc

    processing_options: dict[str, Any] = {}
    if settings.enable_chart_parsing:
        processing_options["specialized_chart_parsing"] = "agentic_plus"

    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix or ".png") as temp_file:
        temp_file.write(image_bytes)
        temp_path = temp_file.name

    try:
        client = AsyncLlamaCloud(api_key=api_key)
        uploaded = await client.files.create(file=temp_path, purpose="parse")
        result = await client.parsing.parse(
            file_id=uploaded.id,
            tier=settings.tier.value,
            version="latest",
            processing_options=processing_options,
            expand=["markdown", "items", "text"],
        )

        markdown = extract_markdown_text(result)
        tables = extract_tables(result)
        return ParsedImageResult(
            image_url=image_url,
            filename=filename,
            success=True,
            markdown=markdown,
            tables=tables,
        )
    except Exception as exc:
        return ParsedImageResult(
            image_url=image_url,
            filename=filename,
            success=False,
            error=str(exc),
        )
    finally:
        os.unlink(temp_path)



def extract_markdown_text(result: Any) -> str:
    """Collect markdown text from parse result pages."""
    pages = getattr(getattr(result, "markdown", None), "pages", None)
    if not pages:
        return ""

    markdown_pages: list[str] = []
    for page in pages:
        content = getattr(page, "markdown", None)
        if isinstance(content, str) and content.strip():
            markdown_pages.append(content.strip())

    return "\n\n---\n\n".join(markdown_pages)



def extract_tables(result: Any) -> list[TableResult]:
    """Extract table-like page items from parse result."""
    items_root = getattr(result, "items", None)
    pages = getattr(items_root, "pages", None)
    if not pages:
        return []

    tables: list[TableResult] = []
    for page in pages:
        page_number = int(getattr(page, "page_number", 0) or 0)
        for item in getattr(page, "items", []) or []:
            rows = _normalize_rows(getattr(item, "rows", None))
            if not rows:
                continue

            markdown = _rows_to_markdown(rows)
            bbox = getattr(item, "b_box", None)
            bbox_value = list(bbox) if isinstance(bbox, (list, tuple)) else None
            tables.append(
                TableResult(
                    page_number=page_number,
                    row_count=len(rows),
                    column_count=max((len(row) for row in rows), default=0),
                    markdown=markdown,
                    bbox=bbox_value,
                )
            )

    return tables



def build_combined_markdown(results: list[ParsedImageResult]) -> str:
    """Create a merged markdown document from parsed image results."""
    sections: list[str] = []
    image_index = 1
    for parsed in results:
        if not parsed.success:
            continue

        section_lines = [f"## Image {image_index}: {parsed.filename}", ""]
        if parsed.markdown.strip():
            section_lines.append(parsed.markdown.strip())
        if parsed.tables:
            section_lines.append("")
            section_lines.append("### Detected Tables")
            section_lines.append("")
            for table_index, table in enumerate(parsed.tables, start=1):
                section_lines.append(f"#### Table {table_index} (Page {table.page_number})")
                section_lines.append(table.markdown)
                section_lines.append("")

        sections.append("\n".join(section_lines).strip())
        image_index += 1

    return "\n\n".join(section for section in sections if section.strip())



def _filename_from_url(url: str) -> str:
    """Derive a stable filename from image URL."""
    path = urlparse(url).path
    name = Path(path).name
    return name or "image.png"



def _normalize_rows(raw_rows: Any) -> list[list[str]]:
    """Normalize heterogeneous row representations into list-of-cells."""
    if not raw_rows or not isinstance(raw_rows, list):
        return []

    rows: list[list[str]] = []
    for row in raw_rows:
        if isinstance(row, list):
            rows.append([str(cell).strip() for cell in row])
            continue

        if isinstance(row, dict):
            cells = row.get("cells", [])
            if isinstance(cells, list):
                rows.append([str(cell).strip() for cell in cells])
            continue

        cells = getattr(row, "cells", None)
        if isinstance(cells, list):
            rows.append([str(cell).strip() for cell in cells])

    return [row for row in rows if row]



def _rows_to_markdown(rows: list[list[str]]) -> str:
    """Render table rows to markdown table string."""
    if not rows:
        return ""

    header = rows[0]
    body = rows[1:] if len(rows) > 1 else []

    def to_row(cells: list[str], width: int) -> str:
        padded = cells + [""] * (width - len(cells))
        return "| " + " | ".join(cell.replace("\n", " ") for cell in padded) + " |"

    width = max(len(row) for row in rows)
    lines = [to_row(header, width), "| " + " | ".join(["---"] * width) + " |"]
    lines.extend(to_row(row, width) for row in body)
    return "\n".join(lines)
