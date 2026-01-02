# AI Models & Architecture Explained

## Overview
DocuMind AI uses a multi-model architecture to handle different aspects of the pipeline: **Understanding**, **Sorting**, and **Answering**. This document explains the role of each model.

## 1. The Embedding Model: `all-MiniLM-L6-v2`
**Role:** "The Librarian" (Search & Retrieval)

This is a specific model used by our Vector Database (ChromaDB). It does NOT generate text. Its only job is to convert text into numbers (vectors).
*   **How it works:** It takes a sentence like "Patient Sunita Sharma" and turns it into a list of 384 numbers.
*   **Why specific queries matter:**
    *   Query: *"Sunita"* -> The model creates a vector map for the concept of "Sunita".
    *   Query: *"Patient Name Sunita"* -> The model creates a vector that is mathematically closer to "Patient Name: Mrs. Sunita Sharma" in the document.
*   **Pros:** Extremely fast, runs locally on CPU/low-resource hardware.
*   **Cons:** Can struggle with short, ambiguous queries (like just a first name) if multiple similar names exist.

## 2. The Response Model: `llama3.2` (V5)
**Role:** "The Generative Brain" (Reading & Writing)

This is the model you chat with. It takes the "Chunks" found by the Librarian and writes a human-readable answer.
*   **Current Model:** `llama3.2:latest` (approx 3 Billion parameters).
*   **Behavior (as seen in your tests):**
    *   It is strict. If the Librarian doesn't give it the right chunk, it says * "I don't have this information."*
    *   If it gets the chunks (like in your successful "Patient details" test), it formats them beautifully into bullet points.

## 3. The Classifier (Hybrid)
**Role:** "The Mail Sorter"

In V5, classification is handled by a **Hierarchy System** (`core/classifier.py`):
1.  **Keyword Scoring:** Checks for ~3000 specific terms ("pathology", "agreement", "python").
2.  **Guardrails:** Strict rules to prevent mistakes (e.g., "Resume" always goes to `Personal`).
3.  **LLM Verification:** Only calls the LLM if the keyword score is equal/confusing.

## Future Architecture (V6)
We are moving to a **Dual LLM Strategy**:

| Feature | Current (V5) | Future (V6) |
| :--- | :--- | :--- |
| **Search** | `all-MiniLM-L6-v2` | `all-MiniLM-L6-v2` (Unchanged, it's efficient) |
| **Sorter** | Keywords | `llama3.2:1b` (Dedicated lightweight AI) |
| **Brain** | `llama3.2:3b` | `llama3.1:8b` (Smarter, better reasoning) |

## Troubleshooting Retrieval
If you get "0% Confidence" / "No info found":
*   **Cause:** The *Librarian* (`all-MiniLM`) couldn't find the page.
*   **Fix:** Be more specific. Instead of "Who is X", ask "Details for Patient X" or "Summary of Contract Y". This gives the embedding model better "hooks" to find the right file.
