# The Unofficial Guide — Project 1

A retrieval-augmented generation (RAG) system for answering questions about first-job success, early-career salaries, onboarding, mentorship, and company culture. The system retrieves relevant advice from 10 curated career guides and grounds LLM responses in those documents only — no hallucination, no general knowledge.

---

## Domain

My domain is new grad job experiences and first-job success guides. These are long-form articles and guides about what early career professionals actually experience during their first job, including salary expectations, onboarding best practices, mentorship strategies, and company culture navigation. This knowledge is valuable because it consolidates fragmented advice spread across career websites, employer blogs, and individual career guides — a new grad can consult this system instead of jumping between 10+ different sources to understand realistic timelines, compensation, and expectations for their first few months. It's hard to find through official channels because HR departments publish role descriptions, not real-world experience narratives, and universities don't teach practical first-job advice.

---

## Document Sources

| # | Source | Type | URL or location |
|---|--------|------|-----------------|
| 1 | Forbes - 4 Pieces Of Advice For Every Grad Starting Their First Job | Article | https://www.forbes.com/sites/andymolinsky/2026/05/10/4-pieces-of-advice-for-every-grad-starting-their-first-job/ |
| 2 | Indeed - Entry-Level Salary: What You Need To Know | Guide | https://www.indeed.com/career-advice/pay-salary/entry-level-salary |
| 3 | Forbes - Salary Shock For Gen Z Graduates | Article | https://www.forbes.com/sites/chriswestfall/2025/05/04/salary-shock-for-gen-z-graduates-what-to-expect-in-entry-level-pay/ |
| 4 | The Balance Money - Types of Employee Benefits and Perks | Guide | https://www.thebalancemoney.com/types-of-employee-benefits-and-perks-2060433 |
| 5 | The Muse - Your Guide to Your First Week on the Job | Guide | https://www.themuse.com/advice/your-guide-to-your-first-week-on-the-job |
| 6 | Indeed - How To Succeed in Your New Job | Guide | https://www.indeed.com/career-advice/starting-new-job/new-job-guide |
| 7 | The Muse - Entry-Level to Exec: Succeeding at Your Company | Guide | https://www.themuse.com/advice/entrylevel-to-exec-the-secret-to-succeeding-at-your-company |
| 8 | LinkedIn Pulse - Life Lessons: What I Learned from My First Job | Article | https://www.linkedin.com/pulse/life-lessons-what-i-learned-from-my-first-job-after-shawn-boss-mba |
| 9 | Berkeley Exec Ed - Your Blueprint for Success: First 90 Days | Guide | https://executive.berkeley.edu/thought-leadership/blog/your-blueprint-success-first-90-days-new-job |
| 10 | Lenny's Newsletter - How to Make an Impact in Your First 90 Days | Newsletter | https://www.lennysnewsletter.com/p/how-to-make-an-impact-in-your-first |

**Coverage:** These 10 sources span salary negotiation, benefits evaluation, onboarding strategies, mentorship, relationship-building, company culture, and 90-day impact frameworks — different perspectives from HR platforms (Indeed, The Balance), career advice sites (The Muse, Forbes), academic institutions (Berkeley), and practitioner newsletters (Lenny's).

---

## Chunking Strategy

**Chunk size:** 400 tokens.

**Overlap:** 100 tokens.

**Why these choices fit your documents:** Career guides are organized into distinct conceptual sections: salary data with state-by-state breakdowns, onboarding week-by-week timelines, mentorship strategies, and 90-day milestones. A 400-token chunk aligns with one cohesive subsection (e.g., "what to do in week 1" or "how to evaluate compensation"), preserving concept boundaries and retrieval precision. The 100-token overlap bridges section transitions to keep related advice connected when a topic spans chunk boundaries. Smaller chunks would fragment concepts; larger chunks would dilute specificity.

**Preprocessing before chunking:**
- Stripped URL headers and author/editor bylines ("Written by...", "Edited by...")
- Removed publication dates ("Updated December 11, 2025")
- Unescaped HTML entities (`&nbsp;` → space, `&#39;` → `'`)
- Filtered metadata fragments (<40 tokens) that are navigation labels ("Article", "In This Article", etc.)
- Collapsed multiple blank lines for cleaner input to LangChain's RecursiveCharacterTextSplitter

**Final chunk count:** 62 chunks across 10 documents (range: 3–15 chunks per document, averaging 330 tokens per chunk). This falls comfortably within the healthy 50–2,000 range; 62 is large enough for semantic signal but small enough for precision.

---

## Embedding Model

**Model used:** `BAAI/bge-small-en-v1.5` via sentence-transformers. 384 dimensions, 512-token max sequence length, runs locally without API keys.

**Why this choice:** The initial spec recommended `all-MiniLM-L6-v2`, which has a 256-token max sequence length. With 400-token chunks, this model would silently truncate ~35% of each chunk before embedding, degrading retrieval precision without visible failure. BGE-small has the same speed and size class (3–4ms inference, 120MB model) but a 512-token capacity, eliminating truncation. It also ranks higher on MTEB retrieval benchmarks, improving semantic matching.

**Production tradeoff reflection:** If cost and latency weren't constraints, I'd prioritize domain-specific accuracy by fine-tuning an embedding model on HR/career corpora. General embeddings conflate career-specific language: "networking" means internal relationship-building for new hires but external outreach for job seekers; "mentorship" can mean career guidance or technical skill transfer. A fine-tuned model would learn these distinctions. Context length is already solved (512 tokens supports our chunking). Multilingual support would help international new grads but isn't critical for V1. Latency is less important—users aren't waiting for real-time responses.

---

## Grounded Generation

**System prompt grounding instruction:**
```
You are a helpful career advice assistant. Your purpose is to answer questions about first jobs and early career success.

CRITICAL RULES:
1. Answer ONLY using the provided documents. Do not use general knowledge or training data.
2. If the documents don't contain enough information to fully answer the question, say: "I don't have enough information on that topic based on the provided documents."
3. Always cite which document(s) you drew the answer from.
4. Be honest about the limits of your knowledge. It's better to say you don't know than to make something up.

You must follow these rules strictly. Grounding is essential.
```

This prompt is implemented in `generator.py` and passed to Groq's llama-3.3-70b-versatile LLM with `temperature=0.3` (favoring factuality over creativity). The instruction is mandatory, not optional. It uses strong language ("CRITICAL RULES", "must follow strictly") to enforce context-only behavior.

**How source attribution is surfaced in the response:**
1. **In the LLM response:** The system prompt instructs the model to cite documents. The model typically writes "According to Document X..." or "Documents Y and Z mention...".
2. **Programmatic source list:** After generation, `generator.py` extracts unique source IDs from the retrieved chunks and returns them in a separate `sources` field. The Gradio interface displays this as "Retrieved from: Documents 2, 5" below the answer.
3. **Double-layer attribution:** Both the answer text and the sources list are shown, so even if the LLM forgets to cite internally, sources are always visible to the user.

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|---|
| 1 | What is the average entry-level salary in the US, and what are three factors that cause variation? | ~$43,262; factors: geography, industry, negotiation; Gen Z expects $101k vs. reality $68k | $43,262; factors: geography, industry/role, employer. Documents mention range $40-62k but missing Gen Z expectation gap. | Relevant | Accurate |
| 2 | What are the top 5 things new hires should focus on during their first week? | Be observant, offer to help, find mentor, keep boss informed, don't compare | Absorb culture, introduce yourself, seek colleague, navigate workplace, add value. Semantically similar but different phrasing; missing "don't compare to previous jobs" explicitly. | Relevant | Partially accurate |
| 3 | How should a new employee approach building internal relationships and finding a mentor in their first 90 days? | Volunteer for cross-team, ask meaningful questions, schedule check-ins with manager, identify key stakeholders, seek mentors | Be proactive, find mentor, don't rely only on mentor, mingle/socialize, build connections, observe leadership. Covered mentorship and relationship-building but missed specific actions like "volunteer for cross-team projects" and "scheduled check-ins with manager". | Relevant | Partially accurate |
| 4 | What components beyond base salary should you evaluate when comparing job offers? | Health insurance, 401k, PTO, bonuses, stock, tuition reimbursement, professional development, remote flexibility; ~30%+ of base | Benefits, vacation, culture, perks, resume impact, mission/values, growth opportunities. Too vague and generic; missing specific components (401k, stock options, tuition reimbursement) and the quantification (30%+ of base). | Partially relevant | Partially accurate |
| 5 | What are three common mistakes new grads make in their first months? How to avoid? | Comparing unfairly, proving too fast instead of learning, not asking questions; emphasize patience, humility, explicit help-seeking | Not being reliable/missing deadlines, overcommitting, being afraid to speak up. Related themes but different mistakes—overcommitting touches "trying too hard" but reliability and speaking up don't align with expected mistakes. | Relevant | Partially accurate |

---

## Failure Case Analysis

**Question that failed:** Question 5. "What are three common mistakes new grads make in their first months, and how should they avoid them?"

**What the system returned:** 
The system retrieved Documents 1, 5, and 6, and returned: (1) Not being reliable / missing deadlines, (2) Overcommitting themselves, (3) Being afraid to speak up. To avoid them: focus on reliability, time management, and contributing to the team.

**Expected answer (from evaluation plan):** 
Comparing yourself to others unfairly, trying to prove yourself too fast instead of learning, and not asking questions. Should emphasize patience, humility, and seeking help explicitly.

**Root cause (tied to a specific pipeline stage):**
This is a corpus-evaluation mismatch, not a system failure. The retrieval and generation are working correctly—the system is retrieving from Documents 1, 5, and 6 and accurately summarizing their content. However, those documents discuss different mistakes than the evaluation plan expected. The evaluation plan assumed the corpus would cover "comparing yourself to others" and "proving yourself too fast," but the documents focus on "reliability," "workload balance," and "speaking up." This reveals that the evaluation plan was written without fully verifying the corpus content matched the expected topics. The system is grounded and accurate to its sources; the sources just don't contain what the evaluation expected.

**What you would change to fix it:**
1. **For future projects:** Before writing evaluation questions, analyze the actual corpus content to ensure questions align with what's actually documented. Use the documents themselves to generate evaluation questions, rather than writing questions speculatively.
2. **For this project:** Accept this as a valid failure case that teaches a valuable lesson: **good evaluation requires understanding your corpus first**. The system performed as designed; the mismatch is in planning, not execution.
3. **Optional enhancement:** If the mistakes topic is important, add sources that specifically discuss comparison anxiety and impostor syndrome among new grads (e.g., articles on psychological safety or first-job pressure).

---

## Spec Reflection

**One way the spec helped you during implementation:**

The chunking strategy spec forced me to think concretely about token boundaries matching my embedding model's capacity. Rather than choosing chunk size arbitrarily, I had to ask: "What's the max sequence length of my embedding model?" (all-MiniLM: 256 tokens). This constraint led me to discover that the recommended default model couldn't handle my 400-token chunks—they'd silently truncate. I replaced it with bge-small (512-token capacity) and updated the spec to document why. This decision-forcing was valuable: I avoided a subtle, hard-to-debug truncation bug that would have degraded retrieval quality invisibly. The spec's insistence on documenting "why these choices fit your documents" pushed me beyond "400 tokens sounds reasonable" to "400 tokens aligns with section boundaries AND fits my embedding model's capacity."

**One way your implementation diverged from the spec, and why:**

The spec recommended `all-MiniLM-L6-v2` as the "recommended default" embedding model. I diverged to `bge-small-en-v1.5` because the spec was generic, not domain-specific. The recommended model has a hard constraint (256-token max) that conflicts with my designed chunk size (400 tokens). Rather than reverting to a smaller chunk size (which would fragment my career-guide domain into more pieces), I chose a larger embedding model that supports the full 400-token chunks. The spec was written for general RAG systems; my implementation prioritized my specific domain's needs. This was the right tradeoff: retrieval quality improved, and the spec explicitly says to update the approach "if you change your approach during implementation" — which I documented in planning.md.

---

## AI Usage

**Instance 1: Code generation for chunking pipeline**

- *What I gave the AI:* My planning.md's Chunking Strategy section (400 tokens, 100 overlap, recursive sentence-boundary splitting) and a request to implement the ingestion and chunking code using LangChain's RecursiveCharacterTextSplitter with the embedding model's tokenizer.
- *What it produced:* A complete `ingest.py` script with `load_documents()`, `clean_text()`, and `chunk_documents()` functions. The clean_text() function removed common boilerplate (author bylines, publication dates). The chunker used LangChain correctly but with basic regex cleaning.
- *What I changed or overrode:* (1) Enhanced the cleaning regex to catch more boilerplate patterns (HTML entities like `&nbsp;`, contributor labels like "Contributor.", metadata like "Updated December 11, 2025"). (2) Added a minimum token count filter (`<40 tokens = skip`) to remove metadata fragments that were slipping through. (3) Refactored the output to include URL metadata extraction from document headers. The AI's foundation was sound; the improvements were targeted cleanup for my specific document types.

**Instance 2: Retrieval and grounded generation implementation**

- *What I gave the AI:* My planning.md's Retrieval Approach section (bge-small model, top-k=7, ChromaDB), the architecture diagram, and a detailed prompt requesting `retrieve()` and `generate()` functions that enforce grounding (answers from context only, source attribution, decline to answer out-of-domain questions).
- *What it produced:* A `retriever.py` that correctly interfaced with ChromaDB (using SentenceTransformerEmbeddingFunction, cosine distance). A `generator.py` that called retrieve(), formatted context, and passed it to Groq with a reasonable grounding prompt.
- *What I changed or overrode:* (1) Strengthened the system prompt with CRITICAL RULES language and explicit "I don't have enough information" fallback (the AI's version was more suggestive than mandatory). (2) Added a programmatic source extraction layer that always surfaces sources independently of whether the LLM cites them (the AI relied on the model to cite, which is less reliable). (3) Fixed the Gradio interface to populate the question input field when example buttons are clicked, not just execute the query. The AI provided the correct APIs and structure; I hardened the grounding mechanism and improved UX.
