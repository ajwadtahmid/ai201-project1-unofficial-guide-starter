# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->

My domain is new grad job experiences and first-job success guides. They are long-form articles and guides about what early career professionals actually experience during their first job, including salary expectations, onboarding, mentorship, and company culture. This knowledge is valuable but fragmented across career advice sites, employer blogs, and individual career guides. A consolidated resource saves new grads from jumping between 10+ different sources to understand realistic timelines, compensation, and what to expect in their first few months.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Forbes - 4 Pieces Of Advice For Every Grad Starting Their First Job | Long-form essay covering 4 key mindsets for year one: saying yes to uncomfortable situations, observing office dynamics before acting, following curiosity, and being reliable. Focus on soft skills and self-awareness. | https://www.forbes.com/sites/andymolinsky/2026/05/10/4-pieces-of-advice-for-every-grad-starting-their-first-job/ |
| 2 | Indeed - Entry-Level Salary: What You Need To Know | Comprehensive guide covering average entry-level salary ($43,262), variation by state and profession, how to increase earning potential, and salary negotiation tips. Includes state-by-state breakdown and industry comparisons. | https://www.indeed.com/career-advice/pay-salary/entry-level-salary |
| 3 | Forbes - Salary Shock For Gen Z Graduates: What To Expect In Entry Level Pay | Research-backed article comparing Gen Z salary expectations ($101,500) vs. reality ($68,400). Covers what Gen Z values in jobs (remote work, flexibility), AI impact on job market, and practical advice on negotiation and career strategy. | https://www.forbes.com/sites/chriswestfall/2025/05/04/salary-shock-for-gen-z-graduates-what-to-expect-in-entry-level-pay/ |
| 4 | The Balance Money - Types of Employee Benefits and Perks | Comprehensive breakdown of total compensation components beyond base salary: health insurance, retirement plans, PTO, bonuses, stock options, tuition assistance, and more. Structured by benefit type with guidance on evaluating a full compensation package. | https://www.thebalancemoney.com/types-of-employee-benefits-and-perks-2060433 |
| 5 | The Muse - Your Guide to Your First Week on the Job | Practical do's and don'ts for the first week: be a sponge, offer to help, find a mentor, keep boss informed, and avoid comparing to previous jobs. Covers office culture absorption and relationship building strategies. | https://www.themuse.com/advice/your-guide-to-your-first-week-on-the-job |
| 6 | Indeed - How To Succeed in Your New Job: First Week, 30 and 90 Days | Comprehensive milestone-based guide breaking down success strategies for week 1, month 1, and 90 days. Covers introductions, learning workplace navigation, understanding team dynamics, adding value, and taking ownership of your role. | https://www.indeed.com/career-advice/starting-new-job/new-job-guide |
| 7 | The Muse - Entry-Level to Exec: The Secret to Succeeding at Your Company | Guide on building internal relationships and visibility after being hired: volunteering for cross-team projects, finding a mentor, asking meaningful questions, and staying connected with your manager. Focused on post-hire career growth within a company. | https://www.themuse.com/advice/entrylevel-to-exec-the-secret-to-succeeding-at-your-company |
| 8 | LinkedIn Pulse - Life Lessons: What I Learned from My First Job After College | Personal reflection on first-job lessons: embracing mistakes, asking questions, prioritizing soft skills, building an internal network, and setting pace for the long run. Broad audience, conversational tone, practical takeaways structured as numbered lessons. | https://www.linkedin.com/pulse/life-lessons-what-i-learned-from-my-first-job-after-shawn-boss-mba |
| 9 | Berkeley Exec Ed - Your Blueprint for Success: The First 90 Days at a New Job | Blueprint for success in first 90 days: balancing learning vs. action, setting strategic intent, and measuring progress. Well-structured with clear phases. | https://executive.berkeley.edu/thought-leadership/blog/your-blueprint-success-first-90-days-new-job |
| 10 | Lenny's Newsletter - How to Make an Impact in Your First 90 Days | Practical framework for new employees to make an immediate impression: understanding priorities, building relationships, identifying quick wins, and establishing a feedback loop with your manager. | https://www.lennysnewsletter.com/p/how-to-make-an-impact-in-your-first |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:** 400 tokens

**Overlap:** 100 tokens

**Reasoning:** These guides are organized into distinct sections (salary/compensation, onboarding, mentorship, company culture, 90-day milestones). A 400-token chunk aligns with one cohesive subsection, preserving concept boundaries while maintaining retrieval precision. The 100-token overlap bridges section transitions to keep related advice connected. Smaller chunks would fragment concepts; larger chunks would dilute precision.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** all-MiniLM-L6-v2 via sentence-transformers

**Top-k:** 7

**Production tradeoff reflection:** If cost weren't a constraint, I'd prioritize domain-specific accuracy. General embeddings conflate career-specific language: "networking" in the context of new hires (internal relationship-building) vs. job seekers (external outreach), or "mentorship" as career guidance vs. technical skill transfer. A model fine-tuned on HR/career corpora would distinguish these nuances. Context length is secondary—my chunking strategy already handles long articles. Latency doesn't matter; users aren't waiting for real-time responses. Multilingual support could be useful for international new grads but isn't critical for V1. 

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What is the average entry-level salary in the US, and what are three factors that cause variation? | ~$43,000-$45,000 base; variation by state, industry/profession, and individual negotiation. Sources should cite Indeed and mention that Gen Z expects $101k but reality is ~$68k. |
| 2 | What are the top 5 things new hires should focus on during their first week? | Be observant, offer to help, find a mentor, keep boss informed, don't compare to previous jobs. Should emphasize listening and relationship-building over proving yourself. |
| 3 | How should a new employee approach building internal relationships and finding a mentor in their first 90 days? | Volunteer for cross-team projects, ask meaningful questions about colleagues' work, schedule regular check-ins with manager, identify key stakeholders, and proactively seek out potential mentors. |
| 4 | What components beyond base salary should you evaluate when comparing job offers? | Health insurance, 401(k) matching, PTO, bonuses, stock options, tuition reimbursement, professional development, remote work flexibility. Total compensation often comprises 30%+ of base salary. |
| 5 | What are three common mistakes new grads make in their first months, and how should they avoid them? | Comparing yourself to others unfairly, trying to prove yourself too fast instead of learning, and not asking questions. Should emphasize patience, humility, and asking for help explicitly. |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. Salary and compensation data: My sources are mainly 2025-2026 salary data. There is a chance this will be stale as time goes on and the model will confidently return them. Also, if a user asks a query like "average salary for finance roles," it could return general new grad finance salary instead of specifically for first-year analysts, which is significantly lower than experienced finance professionals. The vice-versa could happen too.

2. Off-topic but plausible retrieval: Sources like "Life Lessons from My First Job" and "How to Make an Impact" are broad guides covering mentorship, soft skills, company culture, and work pace. A query like "how do I handle a difficult coworker?" might retrieve chunks about "building relationships" or "asking meaningful questions" that are tangentially related but don't directly address conflict. The system returns adjacent advice that sounds relevant but misses the mark.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

STAGE 1           STAGE 2            STAGE 3              STAGE 4          STAGE 5
Ingestion        Chunking         Embedding +          Retrieval        Generation
                                   Vector Store
   │                │                  │                  │                │
   ├─ Load from     ├─ LangChain       ├─ all-MiniLM-L6   ├─ Cosine        ├─ Groq
   │  /documents/   │  Text Split      │  -v2             │  Similarity    │  llama-3.3
   │                │  (400 tok,       │                  │                │
   │                │   100 overlap)   ├─ ChromaDB        ├─ Top-k=7       │
   │                │                  │  Vector Store    │                │
   v                v                  v                  v                v
[TXT Files] → [Clean Text] → [Vectors + Metadata] → [Ranked Chunks] → [Grounded Answer]

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

I will use Claude to generate the ingestion and chunking script. I'll give it my planning.md (specifically the Chunking Strategy section) and explain that my 10 source documents are already in plain .txt files in the /documents folder. I'll ask Claude to write a Python script that: (1) loads all .txt files from the documents folder, (2) cleans them by removing any remaining formatting or boilerplate, (3) chunks each into 400-token chunks with 100-token overlap using LangChain's RecursiveCharacterTextSplitter, and (4) outputs (source_id, chunk_index, text, metadata) tuples with source filename and chunk position preserved. After generating the script, I'll load one document manually, inspect it for cleanliness, then run the chunking script. I'll print 5 representative chunks from different sources and verify each is self-contained and answerable on its own - no HTML artifacts, fragments, or empty strings. I'll also count total chunks (should be ~30–40 across 10 documents based on corpus analysis) and check that metadata is correctly attached.

**Milestone 4 — Embedding and retrieval:** 

I will use Claude to implement embedding and retrieval. I'll give it my planning.md (point to Retrieval Approach section), my Architecture diagram, and the chunk structure from Milestone 3. I'll ask Claude to write code that: (1) loads the chunks from Milestone 3, (2) embeds each with SentenceTransformer('all-MiniLM-L6-v2'), (3) stores them in ChromaDB with source metadata (document name, chunk position), and (4) implements a retrieve(query, top_k=7) function that embeds the query and returns top-k chunks with distance scores. After reviewing the code to understand the ChromaDB API calls, I'll test retrieval with 3 of my 5 evaluation plan questions. For each query, I'll print the returned chunks and distance scores and verify they're relevant to the question and from expected sources. Good retrieval should have distance scores <0.5 and chunks that clearly match the query; if scores are high (>0.6) or chunks are off-topic, I'll debug by checking chunk content, metadata, and possibly adjusting chunk size.

**Milestone 5 — Generation and interface:**

I will use Claude to wire up generation and the Gradio interface. I'll give it my planning.md (Evaluation Plan section), my Architecture diagram, and the retrieval function from M4. I'll ask Claude to: (1) connect retrieval to the Groq llama-3.3-70b-versatile LLM, (2) write a system prompt that strictly enforces grounding - answers must come from retrieved context only, and the model should say "I don't have enough information" if documents don't cover the query, and (3) build a Gradio web interface with a textbox for questions and output boxes for answer + sources. After reviewing the code to verify grounding is enforced (not just suggested), I'll test end-to-end with 2-3 queries: can each response be traced back to my retrieved chunks? I'll also ask a question my documents don't cover and verify the system declines to answer instead of generating something plausible. Finally, I'll launch the Gradio app and test the interface interactively to ensure it's navigable without explanation.
