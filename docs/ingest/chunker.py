#!/usr/bin/env python3
import os
import re
import argparse


def is_useful_chunk(chunk: str, min_lines: int, min_chars: int) -> bool:
    """
    Determine if a chunk contains enough substance to keep:
      - Strips out lines that look like headers or separators.
      - Checks remaining lines for minimum line count and character count.
    """
    # Remove leading/trailing whitespace and split into lines
    lines = [line.strip() for line in chunk.strip().splitlines()]

    # Drop empty lines and pure delimiter/header lines
    content_lines = [
        line
        for line in lines
        if line and not re.match(r"^(FILE:|=+|---|##\s*\w+)", line)
    ]

    if len(content_lines) < min_lines:
        return False

    total_chars = sum(len(line) for line in content_lines)
    if total_chars < min_chars:
        return False

    return True


def chunk_file(input_path: str, output_dir: str, min_lines: int, min_chars: int):
    """
    Read llm_digest.txt, split into raw chunks, filter, and write out
    only the useful ones into output_dir.
    """
    os.makedirs(output_dir, exist_ok=True)

    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split on lines of ten or more '=' characters
    raw_chunks = re.split(r"^\={10,}\s*$", content, flags=re.MULTILINE)

    saved = 0
    for chunk in raw_chunks:
        if is_useful_chunk(chunk, min_lines, min_chars):
            out_file = os.path.join(output_dir, f"chunk_{saved:03}.txt")
            with open(out_file, "w", encoding="utf-8") as out:
                out.write(chunk.strip() + "\n")
            saved += 1

    print(f"\n✅ Saved {saved} meaningful chunks to {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Chunk llm_digest.txt into content-rich files."
    )
    parser.add_argument(
        "-i",
        "--input",
        default="llm_digest.txt",
        help="Path to the GitIngest digest file.",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        default="chunks",
        help="Directory where filtered chunks will be written.",
    )
    parser.add_argument(
        "--min-lines",
        type=int,
        default=3,
        help="Minimum number of content lines to keep a chunk.",
    )
    parser.add_argument(
        "--min-chars",
        type=int,
        default=50,
        help="Minimum total characters (across content lines) to keep a chunk.",
    )
    args = parser.parse_args()

    chunk_file(
        input_path=args.input,
        output_dir=args.output_dir,
        min_lines=args.min_lines,
        min_chars=args.min_chars,
    )
