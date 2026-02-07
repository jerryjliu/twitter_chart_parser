from types import SimpleNamespace

from models import ParsedImageResult
from services.llamacloud_parser import build_combined_markdown, extract_markdown_text, extract_tables


class FakeRow:
    def __init__(self, cells):
        self.cells = cells


class FakeTableItem:
    def __init__(self, rows, b_box=None):
        self.rows = rows
        self.b_box = b_box


def test_extract_markdown_text_joins_pages() -> None:
    result = SimpleNamespace(
        markdown=SimpleNamespace(
            pages=[
                SimpleNamespace(markdown="Page one"),
                SimpleNamespace(markdown="Page two"),
            ]
        )
    )
    text = extract_markdown_text(result)
    assert "Page one" in text
    assert "Page two" in text
    assert "---" in text


def test_extract_tables_handles_row_objects() -> None:
    result = SimpleNamespace(
        items=SimpleNamespace(
            pages=[
                SimpleNamespace(
                    page_number=1,
                    items=[
                        FakeTableItem(rows=[FakeRow(["A", "B"]), FakeRow(["1", "2"])], b_box=[0, 0, 10, 10]),
                    ],
                )
            ]
        )
    )

    tables = extract_tables(result)
    assert len(tables) == 1
    assert tables[0].row_count == 2
    assert "| A | B |" in tables[0].markdown


def test_build_combined_markdown_skips_failed_items() -> None:
    results = [
        ParsedImageResult(
            image_url="https://pbs.twimg.com/media/1.jpg",
            filename="1.jpg",
            success=True,
            markdown="content",
            tables=[],
        ),
        ParsedImageResult(
            image_url="https://pbs.twimg.com/media/2.jpg",
            filename="2.jpg",
            success=False,
            error="boom",
        ),
    ]

    merged = build_combined_markdown(results)
    assert "Image 1" in merged
    assert "2.jpg" not in merged
