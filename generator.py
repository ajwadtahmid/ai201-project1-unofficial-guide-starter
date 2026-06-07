"""
Milestone 5: Generation with Grounding

Connect retrieval to Groq LLM and enforce grounding:
answers must come ONLY from retrieved context, not LLM training knowledge.
"""

from groq import Groq
from retriever import retrieve
from config import GROQ_API_KEY, LLM_MODEL, N_RESULTS

_client = Groq(api_key=GROQ_API_KEY)


def format_context(retrieved_chunks):
    """
    Format retrieved chunks into a context block for the prompt.
    Each chunk includes its source document and content.
    """
    if not retrieved_chunks:
        return "(No relevant context found)"

    context_parts = []
    for i, chunk in enumerate(retrieved_chunks, 1):
        source = chunk.get("source_id", "Unknown")
        text = chunk.get("text", "")
        context_parts.append(f"[Document {source}]\n{text}")

    return "\n\n".join(context_parts)


def extract_sources(retrieved_chunks):
    """Extract unique source document IDs from retrieved chunks."""
    sources = set()
    for chunk in retrieved_chunks:
        source_id = chunk.get("source_id")
        if source_id:
            sources.add(source_id)
    return sorted(list(sources))


def ask(question):
    """
    End-to-end query → retrieval → grounded generation → response.

    Returns:
        dict with keys:
            - "answer": str, the grounded response
            - "sources": list of source_ids the answer came from
    """
    # Step 1: Retrieve relevant chunks
    retrieved_chunks = retrieve(question, n_results=N_RESULTS)

    # Step 2: Extract sources and format context
    sources = extract_sources(retrieved_chunks)
    context = format_context(retrieved_chunks)

    # Step 3: Define grounding prompt
    # This prompt is the CORE of the system — it must enforce context-only answers
    system_prompt = """You are a helpful career advice assistant. Your purpose is to answer questions about first jobs and early career success.

CRITICAL RULES:
1. Answer ONLY using the provided documents. Do not use general knowledge or training data.
2. If the documents don't contain enough information to fully answer the question, say: "I don't have enough information on that topic based on the provided documents."
3. Always cite which document(s) you drew the answer from.
4. Be honest about the limits of your knowledge. It's better to say you don't know than to make something up.

You must follow these rules strictly. Grounding is essential."""

    # Step 4: Call Groq LLM with context + grounding
    try:
        response = _client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": f"""Here are the relevant documents:

{context}

Question: {question}

Answer using ONLY the above documents. Cite which document(s) you used.""",
                },
            ],
            temperature=0.3,  # Low temperature = more factual, less creative
            max_tokens=512,
        )

        answer = response.choices[0].message.content

        return {
            "answer": answer,
            "sources": sources,
        }

    except Exception as e:
        return {
            "answer": f"Error generating response: {str(e)}",
            "sources": [],
        }
