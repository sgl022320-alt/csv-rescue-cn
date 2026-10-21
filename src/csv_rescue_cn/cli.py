"""Command line interface: csv-rescue in.csv -o out.csv [--dedupe] [--dry-run]"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .core import convert_file, detect_encoding


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="csv-rescue",
        description="Fix garbled (mojibake) CSV files: detect GBK/GB18030/Big5/UTF-8, "
        "rewrite as clean UTF-8, optionally trim cells and drop duplicate rows.",
    )
    p.add_argument("input", help="Input CSV file")
    p.add_argument("-o", "--output", help="Output file (default: <input>.utf8.csv)")
    p.add_argument("--dedupe", action="store_true", help="Remove duplicate rows (keeps first)")
    p.add_argument("--no-trim", action="store_true", help="Do not strip whitespace from cells")
    p.add_argument("--excel-bom", action="store_true",
                   help="Write UTF-8 with BOM so Excel opens Chinese text correctly")
    p.add_argument("--dry-run", action="store_true",
                   help="Only report detected encoding / delimiter, write nothing")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    src = Path(args.input)
    if not src.is_file():
        print(f"error: file not found: {src}", file=sys.stderr)
        return 2
    if args.dry_run:
        enc = detect_encoding(src.read_bytes())
        print(f"input: {src}\ndetected encoding: {enc}\n(dry-run, nothing written)")
        return 0
    out = Path(args.output) if args.output else src.with_suffix(".utf8.csv")
    if out.resolve() == src.resolve():
        print("error: output must differ from input (we never overwrite the original)",
              file=sys.stderr)
        return 2
    stats = convert_file(src, out, trim=not args.no_trim,
                         dedupe=args.dedupe, excel_bom=args.excel_bom)
    print(f"input encoding : {stats.source_encoding} (delimiter {stats.delimiter!r})")
    print(f"rows           : {stats.rows_in} -> {stats.rows_out} "
          f"(duplicates removed: {stats.duplicates_removed}, "
          f"empty removed: {stats.empty_rows_removed})")
    print(f"written        : {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
