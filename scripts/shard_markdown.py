#!/usr/bin/env python3
"""
Markdown Document Sharding Tool
Intelligently splits large markdown files into LLM-friendly chunks
while preserving structure, context, and readability.
"""

import re
import argparse
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class MarkdownChunk:
    """Represents a chunk of the markdown document"""
    chunk_number: int
    title: str
    content: str
    headers_context: List[str]  # Breadcrumb of headers
    token_estimate: int
    
    def __str__(self):
        return f"Chunk {self.chunk_number}: {self.title} (~{self.token_estimate} tokens)"


class MarkdownSharder:
    """Shards markdown documents into manageable chunks"""
    
    def __init__(self, max_tokens: int = 4000, overlap_tokens: int = 200):
        """
        Initialize the sharder
        
        Args:
            max_tokens: Maximum tokens per chunk (default: 4000)
            overlap_tokens: Tokens to overlap between chunks for context (default: 200)
        """
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens
        self.header_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count (rough approximation: 1 token ≈ 4 characters)
        
        Args:
            text: Text to estimate
            
        Returns:
            Estimated token count
        """
        return len(text) // 4
    
    def extract_sections(self, content: str) -> List[Dict]:
        """
        Extract sections based on markdown headers
        
        Args:
            content: Full markdown content
            
        Returns:
            List of sections with headers and content
        """
        sections = []
        lines = content.split('\n')
        current_section = {
            'level': 0,
            'title': 'Document Header',
            'content': [],
            'start_line': 0
        }
        header_stack = []
        
        for i, line in enumerate(lines):
            header_match = self.header_pattern.match(line)
            
            if header_match:
                # Save previous section
                if current_section['content']:
                    current_section['content'] = '\n'.join(current_section['content'])
                    current_section['headers_context'] = list(header_stack)
                    sections.append(current_section)
                
                # Start new section
                level = len(header_match.group(1))
                title = header_match.group(2)
                
                # Update header stack
                header_stack = [h for h in header_stack if h['level'] < level]
                header_stack.append({'level': level, 'title': title})
                
                current_section = {
                    'level': level,
                    'title': title,
                    'content': [line],
                    'start_line': i
                }
            else:
                current_section['content'].append(line)
        
        # Add last section
        if current_section['content']:
            current_section['content'] = '\n'.join(current_section['content'])
            current_section['headers_context'] = list(header_stack)
            sections.append(current_section)
        
        return sections
    
    def create_chunks(self, sections: List[Dict]) -> List[MarkdownChunk]:
        """
        Create chunks from sections, respecting token limits
        
        Args:
            sections: List of document sections
            
        Returns:
            List of MarkdownChunk objects
        """
        chunks = []
        current_chunk_content = []
        current_chunk_tokens = 0
        current_headers = []
        chunk_number = 1
        
        for section in sections:
            section_tokens = self.estimate_tokens(section['content'])
            
            # Build context header
            context_header = self._build_context_header(section.get('headers_context', []))
            context_tokens = self.estimate_tokens(context_header)
            
            # If section is too large, it needs to be split
            if section_tokens > self.max_tokens:
                # Save current chunk if any
                if current_chunk_content:
                    chunks.append(self._create_chunk(
                        chunk_number,
                        current_headers,
                        '\n\n'.join(current_chunk_content),
                        current_chunk_tokens
                    ))
                    chunk_number += 1
                    current_chunk_content = []
                    current_chunk_tokens = 0
                
                # Split large section
                sub_chunks = self._split_large_section(section, chunk_number)
                chunks.extend(sub_chunks)
                chunk_number += len(sub_chunks)
                continue
            
            # Check if adding this section exceeds limit
            if current_chunk_tokens + section_tokens + context_tokens > self.max_tokens and current_chunk_content:
                # Save current chunk
                chunks.append(self._create_chunk(
                    chunk_number,
                    current_headers,
                    '\n\n'.join(current_chunk_content),
                    current_chunk_tokens
                ))
                chunk_number += 1
                
                # Start new chunk with overlap
                if self.overlap_tokens > 0 and current_chunk_content:
                    overlap_content = current_chunk_content[-1]
                    overlap_tokens = self.estimate_tokens(overlap_content)
                    if overlap_tokens <= self.overlap_tokens:
                        current_chunk_content = [overlap_content]
                        current_chunk_tokens = overlap_tokens
                    else:
                        current_chunk_content = []
                        current_chunk_tokens = 0
                else:
                    current_chunk_content = []
                    current_chunk_tokens = 0
            
            # Add section to current chunk
            section_with_context = context_header + '\n\n' + section['content']
            current_chunk_content.append(section_with_context)
            current_chunk_tokens += section_tokens + context_tokens
            current_headers = section.get('headers_context', [])
        
        # Add final chunk
        if current_chunk_content:
            chunks.append(self._create_chunk(
                chunk_number,
                current_headers,
                '\n\n'.join(current_chunk_content),
                current_chunk_tokens
            ))
        
        return chunks
    
    def _build_context_header(self, headers_context: List[Dict]) -> str:
        """Build breadcrumb header from context"""
        if not headers_context:
            return ""
        
        breadcrumb = " > ".join([h['title'] for h in headers_context])
        return f"<!-- Context: {breadcrumb} -->"
    
    def _create_chunk(self, number: int, headers: List[Dict], content: str, tokens: int) -> MarkdownChunk:
        """Create a MarkdownChunk object"""
        title = headers[-1]['title'] if headers else "Document Start"
        headers_list = [h['title'] for h in headers]
        
        return MarkdownChunk(
            chunk_number=number,
            title=title,
            content=content,
            headers_context=headers_list,
            token_estimate=tokens
        )
    
    def _split_large_section(self, section: Dict, start_chunk_number: int) -> List[MarkdownChunk]:
        """Split a large section into multiple chunks"""
        chunks = []
        content = section['content']
        paragraphs = content.split('\n\n')
        
        current_chunk = []
        current_tokens = 0
        chunk_num = start_chunk_number
        
        for para in paragraphs:
            para_tokens = self.estimate_tokens(para)
            
            if current_tokens + para_tokens > self.max_tokens and current_chunk:
                # Save current chunk
                chunks.append(self._create_chunk(
                    chunk_num,
                    section.get('headers_context', []),
                    '\n\n'.join(current_chunk),
                    current_tokens
                ))
                chunk_num += 1
                current_chunk = []
                current_tokens = 0
            
            current_chunk.append(para)
            current_tokens += para_tokens
        
        # Add final chunk
        if current_chunk:
            chunks.append(self._create_chunk(
                chunk_num,
                section.get('headers_context', []),
                '\n\n'.join(current_chunk),
                current_tokens
            ))
        
        return chunks
    
    def shard_file(self, input_path: Path, output_dir: Path) -> List[MarkdownChunk]:
        """
        Shard a markdown file into chunks
        
        Args:
            input_path: Path to input markdown file
            output_dir: Directory to save chunks
            
        Returns:
            List of created chunks
        """
        # Read input file
        content = input_path.read_text(encoding='utf-8')
        
        # Extract sections
        sections = self.extract_sections(content)
        
        # Create chunks
        chunks = self.create_chunks(sections)
        
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save chunks
        for chunk in chunks:
            chunk_filename = f"chunk_{chunk.chunk_number:03d}_{self._sanitize_filename(chunk.title)}.md"
            chunk_path = output_dir / chunk_filename
            
            # Add metadata header
            metadata = f"""---
chunk: {chunk.chunk_number}
total_chunks: {len(chunks)}
title: {chunk.title}
context: {" > ".join(chunk.headers_context)}
estimated_tokens: {chunk.token_estimate}
source: {input_path.name}
---

"""
            
            full_content = metadata + chunk.content
            chunk_path.write_text(full_content, encoding='utf-8')
            print(f"Created: {chunk_filename}")
        
        # Create index file
        self._create_index(chunks, output_dir, input_path)
        
        return chunks
    
    def _sanitize_filename(self, title: str) -> str:
        """Sanitize title for use in filename"""
        # Remove special characters and limit length
        sanitized = re.sub(r'[^\w\s-]', '', title)
        sanitized = re.sub(r'[-\s]+', '_', sanitized)
        return sanitized[:50].lower()
    
    def _create_index(self, chunks: List[MarkdownChunk], output_dir: Path, source_file: Path):
        """Create an index file listing all chunks"""
        index_path = output_dir / "README.md"
        
        index_content = f"""# Document Chunks Index

**Source Document:** `{source_file.name}`
**Total Chunks:** {len(chunks)}
**Max Tokens per Chunk:** {self.max_tokens}
**Overlap Tokens:** {self.overlap_tokens}

## Chunks Overview

| Chunk | Title | Context | Est. Tokens |
|-------|-------|---------|-------------|
"""
        
        for chunk in chunks:
            context = " > ".join(chunk.headers_context[-2:]) if len(chunk.headers_context) > 1 else chunk.headers_context[0] if chunk.headers_context else "N/A"
            filename = f"chunk_{chunk.chunk_number:03d}_{self._sanitize_filename(chunk.title)}.md"
            index_content += f"| [{chunk.chunk_number}](./{filename}) | {chunk.title} | {context} | {chunk.token_estimate} |\n"
        
        index_content += f"""

## Reading Order

It's recommended to read the chunks in numerical order to maintain narrative flow and context.

## Token Distribution

- **Total Estimated Tokens:** {sum(c.token_estimate for c in chunks)}
- **Average Tokens per Chunk:** {sum(c.token_estimate for c in chunks) // len(chunks)}
- **Largest Chunk:** {max(chunks, key=lambda c: c.token_estimate).chunk_number} ({max(c.token_estimate for c in chunks)} tokens)
- **Smallest Chunk:** {min(chunks, key=lambda c: c.token_estimate).chunk_number} ({min(c.token_estimate for c in chunks)} tokens)

---
*Generated by Markdown Sharding Tool*
"""
        
        index_path.write_text(index_content, encoding='utf-8')
        print(f"\nCreated index: README.md")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Shard large markdown files into LLM-friendly chunks"
    )
    parser.add_argument(
        "input_file",
        type=Path,
        help="Path to input markdown file"
    )
    parser.add_argument(
        "-o", "--output-dir",
        type=Path,
        help="Output directory for chunks (default: <input_file>_chunks)"
    )
    parser.add_argument(
        "-t", "--max-tokens",
        type=int,
        default=4000,
        help="Maximum tokens per chunk (default: 4000)"
    )
    parser.add_argument(
        "-l", "--overlap",
        type=int,
        default=200,
        help="Overlap tokens between chunks (default: 200)"
    )
    
    args = parser.parse_args()
    
    # Validate input file
    if not args.input_file.exists():
        print(f"Error: Input file not found: {args.input_file}")
        return 1
    
    # Determine output directory
    if args.output_dir:
        output_dir = args.output_dir
    else:
        output_dir = args.input_file.parent / "chunks"
    
    # Create sharder and process file
    sharder = MarkdownSharder(max_tokens=args.max_tokens, overlap_tokens=args.overlap)
    
    print(f"Sharding: {args.input_file}")
    print(f"Output directory: {output_dir}")
    print(f"Max tokens: {args.max_tokens}")
    print(f"Overlap tokens: {args.overlap}")
    print("-" * 60)
    
    chunks = sharder.shard_file(args.input_file, output_dir)
    
    print("-" * 60)
    print(f"\n✓ Successfully created {len(chunks)} chunks")
    print(f"✓ Total estimated tokens: {sum(c.token_estimate for c in chunks)}")
    print(f"✓ Output directory: {output_dir}")
    
    return 0


if __name__ == "__main__":
    exit(main())
