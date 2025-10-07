#!/usr/bin/env python3
import os
import re
import argparse

def load_chunks(chunk_dir):
    """Read all chunk files and return a list of (filename, content)."""
    files = sorted(os.listdir(chunk_dir))
    chunks = []
    for fname in files:
        path = os.path.join(chunk_dir, fname)
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read().strip()
        # Skip purely header-only chunks
        if not text or re.match(r'^FILE:\s*\S+', text) and len(text.splitlines()) == 1:
            continue
        chunks.append((fname, text))
    return chunks

def extract_headings(content):
    """Find all markdown headings for TOC."""
    headings = []
    for line in content.splitlines():
        m = re.match(r'^(#{2,6})\s+(.*)$', line)
        if m:
            level = len(m.group(1)) - 1  # start TOC at level-1
            title = m.group(2).strip()
            # create anchor (GitHub-style)
            anchor = re.sub(r'[^\w\s-]', '', title).lower().replace(' ', '-')
            headings.append((level, title, anchor))
    return headings

def build_readme(chunks, title):
    """Assemble the final README text."""
    # 1) Title
    md = [f"# {title}", ""]
    # 2) Table of Contents
    all_headings = []
    for _, text in chunks:
        all_headings += extract_headings(text)
    if all_headings:
        md.append("## Table of Contents")
        for lvl, text, anchor in all_headings:
            indent = "  " * (lvl - 1)
            md.append(f"{indent}- [{text}](#{anchor})")
        md.append("")

    # 3) Body: just concatenate all chunks in order
    for fname, text in chunks:
        md.append(text)
        md.append("")

    return "\n".join(md).strip() + "\n"

def main():
    p = argparse.ArgumentParser(
        description="Generate a comprehensive README.md from GitIngest chunks."
    )
    p.add_argument(
        "-c", "--chunk-dir",
        default="chunks",
        help="Directory containing chunk_*.txt files"
    )
    p.add_argument(
        "-o", "--output",
        default="README.generated.md",
        help="Path to write the generated README"
    )
    p.add_argument(
        "-t", "--title",
        default=None,
        help="Project title (defaults to first H2 in chunks or output filename)"
    )
    args = p.parse_args()

    chunks = load_chunks(args.chunk_dir)
    if not chunks:
        print("⚠️  No useful chunks found in", args.chunk_dir)
        return

    # Determine title
    project_title = args.title
    if not project_title:
        # look for H2 (## ) in first chunk
        for _, text in chunks:
            for line in text.splitlines():
                m = re.match(r'^##\s+(.*)$', line)
                if m:
                    project_title = m.group(1).strip()
                    break
            if project_title:
                break
        if not project_title:
            project_title = os.path.splitext(args.output)[0]

    readme_text = build_readme(chunks, project_title)

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(readme_text)

    print(f"✅ Generated {args.output} with {len(chunks)} chunks.")

if __name__ == "__main__":
    main()
