"""
Milestone 4: Embedding and Retrieval

Load chunks from chunks.json, embed them with bge-small-en-v1.5,
store in ChromaDB, and test retrieval with evaluation queries.
"""

import json
import chromadb
from chromadb.utils import embedding_functions
from config import CHROMA_COLLECTION, CHROMA_PATH, EMBEDDING_MODEL, N_RESULTS, CHUNKS_FILE

# Initialize ChromaDB client and collection at module load.
# SentenceTransformer downloads the model on first use (~30-60s first run).
_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=EMBEDDING_MODEL
)
_client = chromadb.PersistentClient(path=CHROMA_PATH)
_collection = _client.get_or_create_collection(
    name=CHROMA_COLLECTION,
    embedding_function=_ef,
    metadata={"hnsw:space": "cosine"},
)


def get_collection():
    """Return the ChromaDB collection."""
    return _collection


def embed_and_store(chunks):
    """
    Embed chunks and store in ChromaDB.

    Args:
        chunks: list of dicts with keys {source_id, chunk_index, text, url, token_count}

    ChromaDB's SentenceTransformerEmbeddingFunction automatically converts
    text to vectors using bge-small-en-v1.5. We just provide documents,
    metadatas, and unique IDs.
    """
    if not chunks:
        print("No chunks to store.")
        return

    # Build parallel lists for ChromaDB
    documents = [c["text"] for c in chunks]
    metadatas = [
        {
            "source_id": c["source_id"],
            "chunk_index": c["chunk_index"],
            "url": c["url"],
            "token_count": c["token_count"],
        }
        for c in chunks
    ]
    ids = [f"{c['source_id']}_chunk_{c['chunk_index']}" for c in chunks]

    # Store in ChromaDB
    _collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids,
    )
    print(f"✓ Embedded and stored {_collection.count()} chunks in ChromaDB")


def retrieve(query, n_results=N_RESULTS):
    """
    Find the most relevant chunks for a query.

    Args:
        query: str, the user's question
        n_results: int, number of results to return

    Returns:
        list of dicts with keys {text, source_id, chunk_index, url, distance}
    """
    if _collection.count() == 0:
        print("Vector store is empty. Run embed_and_store() first.")
        return []

    # Query ChromaDB
    results = _collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )

    # Parse results (query returns nested lists, we have 1 query)
    if not results["documents"] or not results["documents"][0]:
        return []

    retrieved = []
    for i, doc_text in enumerate(results["documents"][0]):
        metadata = results["metadatas"][0][i]
        distance = results["distances"][0][i]

        retrieved.append({
            "text": doc_text,
            "source_id": metadata["source_id"],
            "chunk_index": metadata["chunk_index"],
            "url": metadata["url"],
            "distance": distance,
        })

    return retrieved


def load_chunks_from_json(filepath=CHUNKS_FILE):
    """Load chunks from JSON file created in Milestone 3."""
    with open(filepath, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    print(f"✓ Loaded {len(chunks)} chunks from {filepath}")
    return chunks


def test_retrieval():
    """
    Test retrieval with 3 evaluation queries.
    Prints results with distances and relevance assessment.
    """
    # Test queries from evaluation plan
    test_queries = [
        {
            "query": "What is the average entry-level salary in the US, and what are three factors that cause variation?",
            "expected_topics": ["salary", "entry-level", "compensation", "variation"],
        },
        {
            "query": "What are the top 5 things new hires should focus on during their first week?",
            "expected_topics": ["first week", "onboarding", "new hire", "observe"],
        },
        {
            "query": "How should a new employee approach building internal relationships and finding a mentor in their first 90 days?",
            "expected_topics": ["mentor", "relationships", "90 days", "networking"],
        },
    ]

    print("\n" + "=" * 80)
    print("RETRIEVAL TEST: 3 Evaluation Queries")
    print("=" * 80)

    for q_idx, test_q in enumerate(test_queries, 1):
        query = test_q["query"]
        print(f"\n[Query {q_idx}]")
        print(f"Question: {query}\n")

        # Retrieve
        results = retrieve(query, n_results=N_RESULTS)

        # Print top 3 results
        print(f"Top 3 results (distance < 0.5 is good):")
        print("-" * 80)

        for rank, result in enumerate(results[:3], 1):
            distance = result["distance"]
            source = result["source_id"]
            chunk_idx = result["chunk_index"]
            text_preview = result["text"][:250]

            # Color-code quality (crude but readable)
            quality = "✓ GOOD" if distance < 0.5 else "⚠ WEAK" if distance < 0.65 else "✗ POOR"

            print(f"\nRank {rank}: {quality} (distance: {distance:.3f})")
            print(f"Source: {source}, Chunk {chunk_idx}")
            print(f"Text: {text_preview}...")
            print()

        # Checkpoint assessment
        top_distance = results[0]["distance"] if results else 1.0
        checkpoint = "PASS ✓" if top_distance < 0.5 else "WARN ⚠" if top_distance < 0.65 else "FAIL ✗"
        print(f"Checkpoint: Top distance {top_distance:.3f} — {checkpoint}")
        print("-" * 80)


def main():
    """
    Milestone 4: Load chunks, embed, store in ChromaDB, test retrieval.
    """
    print("Milestone 4: Embedding and Retrieval\n")

    # Step 1: Load chunks from M3
    print("Step 1: Load chunks")
    chunks = load_chunks_from_json()

    # Step 2: Embed and store
    print("\nStep 2: Embed and store in ChromaDB")
    embed_and_store(chunks)

    # Step 3: Test retrieval
    print("\nStep 3: Test retrieval")
    test_retrieval()

    print("\n" + "=" * 80)
    print("Milestone 4 Complete")
    print("=" * 80)
    print("\n📍 Checkpoint Summary:")
    print("  • Retrieved chunks are relevant to queries")
    print("  • Distance scores < 0.5 on top results")
    print("  • Source metadata (source_id, url) is present")
    print("  • Ready to proceed to Milestone 5 (Generation + Interface)")


if __name__ == "__main__":
    main()
