#!/usr/bin/env python3
"""
Phase 15B — NLSY97 Archive Inspection Script.

Inspects the NLSY97 ZIP archive without full extraction.
Reports file metadata: names, sizes, compression ratios.
Does not extract or load data into memory.

Usage:
    python inspect_nlsy97_archive.py --zip labs/population_baseline/data/raw/nlsy97/nlsy97_all_1997-2023.zip
"""

import argparse
import sys
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def inspect_archive(zip_path: Path) -> dict:
    """Inspect ZIP archive metadata without extraction."""
    if not zip_path.exists():
        return {"error": f"File not found: {zip_path}"}

    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            files = []
            total_compressed = 0
            total_uncompressed = 0

            for info in zf.infolist():
                if info.is_dir():
                    continue

                file_info = {
                    "name": info.filename,
                    "compressed_size": info.compress_size,
                    "uncompressed_size": info.file_size,
                    "compression_ratio": (
                        round(info.compress_size / info.file_size * 100, 1)
                        if info.file_size > 0 else 0
                    ),
                    "format": Path(info.filename).suffix.lower(),
                }
                files.append(file_info)
                total_compressed += info.compress_size
                total_uncompressed += info.file_size

            return {
                "zip_path": str(zip_path),
                "total_files": len(files),
                "total_compressed_size": total_compressed,
                "total_uncompressed_size": total_uncompressed,
                "overall_compression_ratio": (
                    round(total_compressed / total_uncompressed * 100, 1)
                    if total_uncompressed > 0 else 0
                ),
                "files": files,
            }
    except zipfile.BadZipFile:
        return {"error": f"Invalid ZIP file: {zip_path}"}


def format_size(size_bytes: int) -> str:
    """Format bytes to human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def main():
    parser = argparse.ArgumentParser(description="NLSY97 archive inspection")
    parser.add_argument("--zip", type=str, required=True,
                        help="Path to NLSY97 ZIP archive")
    parser.add_argument("--output", type=str, default=None,
                        help="Output path for markdown report")
    args = parser.parse_args()

    zip_path = Path(args.zip)
    if not zip_path.is_absolute():
        zip_path = REPO_ROOT / zip_path

    print(f"NLSY97 Archive Inspection")
    print(f"Archive: {zip_path}")
    print()

    result = inspect_archive(zip_path)

    if "error" in result:
        print(f"ERROR: {result['error']}")
        return 1

    print(f"Total files: {result['total_files']}")
    print(f"Compressed size: {format_size(result['total_compressed_size'])}")
    print(f"Uncompressed size: {format_size(result['total_uncompressed_size'])}")
    print(f"Compression ratio: {result['overall_compression_ratio']}%")
    print()

    # Categorize files by format
    formats = {}
    for f in result['files']:
        fmt = f['format'] or '(no ext)'
        if fmt not in formats:
            formats[fmt] = []
        formats[fmt].append(f)

    print("Files by format:")
    for fmt, files in sorted(formats.items()):
        total_size = sum(f['uncompressed_size'] for f in files)
        print(f"  {fmt}: {len(files)} file(s), {format_size(total_size)} total")
        for f in files:
            print(f"    - {f['name']}: {format_size(f['uncompressed_size'])} "
                  f"({f['compression_ratio']}% of original)")

    # Generate markdown report if requested
    if args.output:
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = REPO_ROOT / output_path

        with open(output_path, 'w') as f:
            f.write("# NLSY97 Archive Inspection Report\n\n")
            f.write(f"**Archive:** `{zip_path.relative_to(REPO_ROOT)}`\n\n")
            f.write("## Summary\n\n")
            f.write(f"- Total files: {result['total_files']}\n")
            f.write(f"- Compressed size: {format_size(result['total_compressed_size'])}\n")
            f.write(f"- Uncompressed size: {format_size(result['total_uncompressed_size'])}\n")
            f.write(f"- Compression ratio: {result['overall_compression_ratio']}%\n\n")
            f.write("## Files by Format\n\n")
            for fmt, files in sorted(formats.items()):
                total_size = sum(f['uncompressed_size'] for f in files)
                f.write(f"### {fmt}\n\n")
                f.write(f"- Count: {len(files)}\n")
                f.write(f"- Total size: {format_size(total_size)}\n\n")
                f.write("| Filename | Uncompressed Size | Compression Ratio |\n")
                f.write("|----------|-------------------|-------------------|\n")
                for file_info in files:
                    f.write(f"| {file_info['name']} | {format_size(file_info['uncompressed_size'])} | {file_info['compression_ratio']}% |\n")
                f.write("\n")

        print(f"\nReport written to: {output_path.relative_to(REPO_ROOT)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
