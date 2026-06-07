"""
Milestone 3: Document Ingestion and Chunking Pipeline

Load documents from documents/, clean them, and chunk into 400-token pieces
using LangChain's RecursiveCharacterTextSplitter with bge-small-en-v1.5 tokenizer.
"""

import os
import re
import html
import json
from pathlib import Path
from typing import List, Dict
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import DOCS_PATH, EMBEDDING_MODEL, CHUNKS_FILE

CHUNK_SIZE = 400
CHUNK_OVERLAP = 100


def load_documents() -> List[Dict]:
    """
    Load all .txt files from documents/ folder.
    Extract URL metadata from 'URL: ...' header line.
    Returns list of dicts: {filename, source_id, url, raw_text}
    """
    documents = []
    for filename in sorted(os.listdir(DOCS_PATH)):
        if filename.endswith(".txt"):
            filepath = os.path.join(DOCS_PATH, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                raw_text = f.read()

            # Extract URL from first line if present
            lines = raw_text.split("\n")
            url = ""
            text_start = 0
            if lines and lines[0].startswith("URL:"):
                url = lines[0].replace("URL:", "").strip()
                text_start = 1

            # Remove URL header from text
            text_after_url = "\n".join(lines[text_start:])

            documents.append({
                "filename": filename,
                "source_id": filename.replace(".txt", ""),
                "url": url,
                "raw_text": text_after_url,
            })

    print(f"✓ Loaded {len(documents)} documents from {DOCS_PATH}/")
    return documents


def clean_text(text: str) -> str:
    """
    Remove boilerplate, HTML entities, and formatting artifacts.
    Keeps substantive content: article text, titles, key facts.
    """
    # Unescape HTML entities (&nbsp; → space, &#39; → ', &amp; → &, etc.)
    text = html.unescape(text)

    # Remove author/byline boilerplate patterns
    # "ByAuthor Name, Title", "Written by ...", "Edited by ...", etc.
    text = re.sub(r"^(?:By|Written by|Edited by)[A-Za-z\s,\.]+?(?=\n|$)", "", text, flags=re.MULTILINE | re.IGNORECASE)

    # Remove publication date lines (e.g., "May 10, 2026, 09:06am EDT", "Updated December 11, 2025")
    text = re.sub(r"^(?:Updated|Published).*?(?=\n|$)", "", text, flags=re.MULTILINE | re.IGNORECASE)
    text = re.sub(r"^[A-Za-z]+\s+\d+,\s+\d{4}.*?(?=\n|$)", "", text, flags=re.MULTILINE)

    # Remove "+ Follow" or similar social follow buttons
    text = re.sub(r"\+\s*Follow", "", text, flags=re.IGNORECASE)

    # Remove image captions / credit lines (e.g., "getty", "woman graduating from college")
    # Common pattern: short lines that are image descriptions in all-caps or italics-like
    text = re.sub(r"^(?:getty|[A-Z]{2,}|woman [a-z\s]+)$", "", text, flags=re.MULTILINE)

    # Remove contributor / author bio patterns
    text = re.sub(r"^Contributor\.", "", text, flags=re.MULTILINE)
    text = re.sub(r"^Former Contributor\.", "", text, flags=re.MULTILINE)
    text = re.sub(r"^[A-Z][a-z]+ [A-Z][a-z]+(?:,\s*[A-Z\.]+)?\s*(?:headshot)?", "", text, flags=re.MULTILINE)
    text = re.sub(r"^learn about our editorial policies", "", text, flags=re.MULTILINE | re.IGNORECASE)
    text = re.sub(r"^[A-Za-z]+ is (?:one of |a |the ).*?(?:expert|author|founder|journalist)s?\.?$", "", text, flags=re.MULTILINE | re.IGNORECASE)

    # Remove "In This Article" table-of-contents sections and standalone "Article" labels
    text = re.sub(r"^In This Article\s*\n(?:.*?\n)*?(?=\n|\S)", "", text, flags=re.MULTILINE | re.IGNORECASE)
    text = re.sub(r"^\s*Article\s*$", "", text, flags=re.MULTILINE | re.IGNORECASE)

    # Remove markdown-style footnote links like "[1m]"
    text = re.sub(r"\[\d+[a-z]?\]", "", text)

    # Collapse multiple spaces and blank lines
    text = re.sub(r" {2,}", " ", text)  # Multiple spaces → single space
    text = re.sub(r"\n{3,}", "\n\n", text)  # Multiple newlines → double newline

    # Strip leading/trailing whitespace
    text = text.strip()

    return text


def chunk_documents(documents: List[Dict], embed_model) -> List[Dict]:
    """
    Split documents into chunks using LangChain's RecursiveCharacterTextSplitter.
    Uses the embedding model's tokenizer for accurate token-based sizing.

    Returns list of dicts: {source_id, chunk_index, text, url, token_count}
    """
    splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
        embed_model.tokenizer,
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " ", ""],  # Prefer paragraph → sentence → word
        strip_whitespace=True,
    )

    all_chunks = []
    for doc in documents:
        cleaned_text = clean_text(doc["raw_text"])
        splits = splitter.split_text(cleaned_text)

        for chunk_idx, chunk_text in enumerate(splits):
            if len(chunk_text.strip()) > 0:  # Filter empty chunks
                # Count tokens in this chunk
                token_count = len(embed_model.tokenizer.encode(chunk_text))

                # Skip metadata fragments (< 40 tokens is likely just headers/metadata)
                if token_count < 40:
                    continue

                all_chunks.append({
                    "source_id": doc["source_id"],
                    "chunk_index": chunk_idx,
                    "text": chunk_text,
                    "url": doc["url"],
                    "token_count": token_count,
                })

    return all_chunks


def inspect_chunks(documents: List[Dict], chunks: List[Dict]) -> None:
    """
    Print one full cleaned document and 5 sample chunks for quality inspection.
    """
    print("\n" + "=" * 80)
    print("INSPECTION CHECKPOINT 1: One cleaned document")
    print("=" * 80)
    first_doc = documents[0]
    cleaned = clean_text(first_doc["raw_text"])
    print(f"\nDocument: {first_doc['filename']}")
    print(f"URL: {first_doc['url']}")
    print(f"Cleaned text length: {len(cleaned)} chars")
    print("\nFirst 500 characters:")
    print(cleaned[:500])
    print("\n[... document continues ...]")

    print("\n" + "=" * 80)
    print("INSPECTION CHECKPOINT 2: 5 sample chunks")
    print("=" * 80)

    # Pick 5 chunks spread across different documents
    chunk_by_source = {}
    for chunk in chunks:
        sid = chunk["source_id"]
        if sid not in chunk_by_source:
            chunk_by_source[sid] = []
        chunk_by_source[sid].append(chunk)

    # Sample 5 chunks from different sources
    sources = list(chunk_by_source.keys())[:5]
    sample_chunks = [chunk_by_source[src][0] for src in sources]

    for i, chunk in enumerate(sample_chunks, 1):
        print(f"\n[Sample {i}] Source: {chunk['source_id']}, Tokens: {chunk['token_count']}")
        print(f"Text: {chunk['text'][:300]}")
        if len(chunk['text']) > 300:
            print("...")

    print("\n" + "=" * 80)
    print(f"SUMMARY: {len(chunks)} total chunks across {len(documents)} documents")
    print("=" * 80)

    # Token distribution
    token_counts = [c["token_count"] for c in chunks]
    print(f"Chunk token distribution:")
    print(f"  Min: {min(token_counts)}, Max: {max(token_counts)}, Avg: {sum(token_counts)//len(token_counts)}")
    print(f"\nChunks per document:")
    for src in sorted(chunk_by_source.keys()):
        print(f"  {src}: {len(chunk_by_source[src])} chunks")


def save_chunks(chunks: List[Dict], output_file: str = None) -> None:
    """Save chunks to a JSON file for Milestone 4 (embedding/retrieval)."""
    if output_file is None:
        output_file = CHUNKS_FILE
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Saved {len(chunks)} chunks to {output_file}")


def main():
    print("Milestone 3: Document Ingestion and Chunking\n")

    # Step 1: Load documents
    documents = load_documents()

    # Step 2: Initialize embedding model (needed for tokenizer)
    print(f"Loading embedding model: {EMBEDDING_MODEL}")
    embed_model = SentenceTransformer(EMBEDDING_MODEL)
    print(f"✓ Model loaded (max sequence length: {embed_model.max_seq_length} tokens)\n")

    # Step 3: Chunk documents
    print(f"Chunking with: size={CHUNK_SIZE} tokens, overlap={CHUNK_OVERLAP} tokens")
    chunks = chunk_documents(documents, embed_model)
    print(f"✓ Created {len(chunks)} chunks\n")

    # Step 4: Inspect
    inspect_chunks(documents, chunks)

    # Step 5: Save for next milestone
    save_chunks(chunks)


if __name__ == "__main__":
    main()
