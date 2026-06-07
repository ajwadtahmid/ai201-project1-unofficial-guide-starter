"""
Milestone 5: Gradio Web Interface

Query interface for the career advice RAG system.
Enter a question, get a grounded answer with source attribution.
"""

import gradio as gr
from generator import ask
from config import EMBEDDING_MODEL, LLM_MODEL, N_RESULTS


def handle_query(question):
    """
    Handle a user question: retrieve, generate, return question + answer + sources.
    Returns (question, answer, sources_str) so example buttons can populate the input.
    """
    if not question.strip():
        return question, "", "No question provided"

    result = ask(question)
    answer = result["answer"]

    # Format sources as a readable list
    if result["sources"]:
        sources_str = "Documents: " + ", ".join(result["sources"])
    else:
        sources_str = "No sources retrieved"

    return question, answer, sources_str


# Build the Gradio interface
with gr.Blocks(
    title="First Job Success Guide — RAG",
    theme=gr.themes.Soft(primary_hue="blue"),
) as demo:

    # Header
    gr.Markdown("""
    # 💼 First Job Success Guide

    Ask questions about entry-level salaries, onboarding, mentorship, company culture, and the first 90 days.

    **How it works:** Your question is searched against a database of career guides. The answer is grounded in those documents only — no general knowledge, no hallucinations.
    """)

    # Main interface
    with gr.Row():
        with gr.Column(scale=2):
            question_input = gr.Textbox(
                label="Your question",
                placeholder="e.g., What should I focus on during my first week?",
                lines=2,
            )

            ask_button = gr.Button("Ask", variant="primary", size="lg")

            answer_output = gr.Textbox(
                label="Answer",
                lines=8,
                interactive=False,
            )

            sources_output = gr.Textbox(
                label="Retrieved from",
                lines=2,
                interactive=False,
            )

        with gr.Column(scale=1, min_width=220):
            gr.Markdown("""
            ### 📋 Example Questions

            Try asking about:
            """)

            example_questions = [
                "What is the average entry-level salary in the US?",
                "What are the top 5 things to focus on in my first week?",
                "How should I approach building internal relationships?",
                "What should I evaluate beyond base salary?",
                "What are common mistakes new grads make?",
                "How do I find a mentor in my first 90 days?",
                "What does total compensation include?",
                "How can I succeed in my first 30 days?",
            ]

            for i, example in enumerate(example_questions):
                gr.Button(
                    example,
                    size="sm",
                    variant="secondary",
                ).click(
                    handle_query,
                    inputs=gr.Textbox(value=example, visible=False),
                    outputs=[question_input, answer_output, sources_output],
                )

    # Wire up interactions
    ask_button.click(
        handle_query,
        inputs=question_input,
        outputs=[question_input, answer_output, sources_output],
    )

    # Allow pressing Enter to submit
    question_input.submit(
        handle_query,
        inputs=question_input,
        outputs=[question_input, answer_output, sources_output],
    )

    # Footer
    gr.Markdown("""
    ---

    **About this system:**
    - Embedding model: `BAAI/bge-small-en-v1.5`
    - LLM: `llama-3.3-70b-versatile` (via Groq)
    - Retrieved chunks: top-7 (configurable)
    - Grounding: Answers come from documents only. If a question isn't covered, the system will say so.
    """)


if __name__ == "__main__":
    print("\n" + "="*70)
    print("  First Job Success Guide — RAG Interface")
    print("="*70)
    print("\nLaunching Gradio interface...")
    print("Open http://localhost:7860 in your browser\n")
    print(f"Configuration:")
    print(f"  • Embedding: {EMBEDDING_MODEL}")
    print(f"  • LLM: {LLM_MODEL}")
    print(f"  • Top-k: {N_RESULTS}")
    print("="*70 + "\n")

    demo.launch(server_name="localhost", server_port=7860, share=False)
