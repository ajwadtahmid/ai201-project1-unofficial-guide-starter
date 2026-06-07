"""Configuration constants for the RAG pipeline."""

import os
from dotenv import load_dotenv

load_dotenv()

# --- LLM ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LLM_MODEL = "llama-3.3-70b-versatile"

# --- Embeddings ---
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

# --- Vector store ---
CHROMA_COLLECTION = "career_guides"
CHROMA_PATH = "./chroma_db"

# --- Retrieval ---
N_RESULTS = 7  # From planning.md: top_k=7

# --- Documents ---
DOCS_PATH = "./documents"
CHUNKS_FILE = "chunks.json"
