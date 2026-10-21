"""Core logic for csv-rescue-cn.

Detects the encoding of a CSV file (UTF-8 / UTF-8-SIG / GB18030 / Big5),
normalises it to UTF-8, and optionally trims cells and removes duplicate rows.
Zero third-party dependencies: only the Python standard library is used.
"""
from __future__ import annotations

import csv
import io
from dataclasses import dataclass, field
from pathlib import Path

# Order matters: BOM is handled before this list; afterwards try UTF-8 first,
# then GB18030 (a superset of GBK/GB2312, covering most legacy Chinese files).
CANDIDATE_ENCODINGS = ("utf-8", "gb18030", "big5")


@dataclass
class ConvertStats:
    source_encoding: str
    rows_in: int = 0
    rows_out: int = 0
    duplicates_removed: int = 0
    empty_rows_removed: int = 0
    delimiter: str = ","
    warnings: list[str] = field(default_factory=list)


def detect_encoding(raw: bytes) -> str:
    """Return the first candidate encoding that decodes *raw* without errors."""
    if raw.startswith(b"\xef\xbb\xbf"):
        return "utf-8-sig"
    for enc in CANDIDATE_ENCODINGS:
        try:
            raw.decode(enc)
            return enc
        except (UnicodeDecodeError, LookupError):
            continue
    raise ValueError(
        "Could not decode file with any supported encoding "
        f"({', '.join(CANDIDATE_ENCODINGS)}). The file may be binary or corrupted."
    )


def clean_rows(rows, *, trim=True, dedupe=False):
    """Yield cleaned rows; returns (cleaned_rows, duplicates_removed, empty_removed)."""
    seen = set()
    cleaned, dup, empty = [], 0, 0
    for row in rows:
        new_row = [cell.strip() for cell in row] if trim else list(row)
        if not any(cell for cell in new_row):
            empty += 1
            continue
        if dedupe:
            key = tuple(new_row)
            if key in seen:
                dup += 1
                continue
            seen.add(key)
        cleaned.append(new_row)
    return cleaned, dup, empty


def convert_file(input_path, output_path, *, trim=True, dedupe=False, excel_bom=False):
    """Convert *input_path* to a clean UTF-8 CSV at *output_path*. Returns ConvertStats."""
    input_path, output_path = Path(input_path), Path(output_path)
    raw = input_path.read_bytes()
    encoding = detect_encoding(raw)
    text = raw.decode(encoding)

    try:
        dialect = csv.Sniffer().sniff(text[:8192], delimiters=",;\t|")
        delimiter = dialect.delimiter
    except csv.Error:
        delimiter = ","

    reader = csv.reader(io.StringIO(text), delimiter=delimiter)
    rows = list(reader)
    cleaned, dup, empty = clean_rows(rows, trim=trim, dedupe=dedupe)

    out_encoding = "utf-8-sig" if excel_bom else "utf-8"
    with output_path.open("w", encoding=out_encoding, newline="") as f:
        csv.writer(f, delimiter=",", lineterminator="\n").writerows(cleaned)

    return ConvertStats(
        source_encoding=encoding,
        rows_in=len(rows),
        rows_out=len(cleaned),
        duplicates_removed=dup,
        empty_rows_removed=empty,
        delimiter=delimiter,
    )
