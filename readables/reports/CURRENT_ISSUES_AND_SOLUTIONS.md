# Current Response Issues & Solutions

This document summarizes the limitations observed during the V5 Testing Phase and the technical solutions required for V6/Production.

## 1. The "Math Blindness" Problem (Reasoning)
*   **Symptom:** AI correctly extracts "11.2" and "Range 12-15" but concludes "It is Normal".
*   **Root Cause:** The 3B parameter model (Llama 3.2) captures *patterns* but lacks *logic circuits* for greater-than/less-than comparison. It sees the numbers are close and hallucinates "safe".
*   **Solution (Future V6):** **Upgrade to a Reasoning Model**.
    *   **Decision:** Stick with `Llama 3.2` for V5.
    *   **Impact:** We accept that complex math/logic queries may be inaccurate.
    *   **Tool:** Larger Reasoning Model (TBD for V6).

## 2. The "Keyword Overshadowing" Problem (Retrieval)
*   **Symptom:** Query "Port 80 error" retrieved the SOW (Project Management) file first, instead of the Log file.
*   **Root Cause:** The SOW had the word "Deployment" many times. The vector search (`all-MiniLM`) prioritized the *theme* of deployment over the *specific* error detail.
*   **Solution:** **Implement Re-ranking**.
    *   **Tool:** `CrossEncoder` (e.g., `ms-marco-MiniLM`).
    *   **Mechanism:** After getting the top 20 "thematic" matches, a second model strictly grades them: "Does this chunk actually answer the specific question?" and discards the SOW.

## 3. The "Name Ambiguity" Problem (Sensitivity)
*   **Symptom:** "Who is Sunita" failed, but "Patient Sunita" worked.
*   **Root Cause:** The embedding model is small. "Sunita" (name) and "Sunita" (in text) had a weak vector overlap compared to noise.
*   **Solution:** **Query Expansion** or **Larger Embeddings**.
    *   **Mechanism (Query Expansion):** Before searching, the LLM rewrites the user's "Who is Sunita?" to "Find patient details, medical reports, or documents mentioning Sunita Sharma". This gives the search engine more hooks.

## Summary Matrix

| Issue | Difficulty | Fix Priority | Solution Component |
| :--- | :--- | :--- | :--- |
| **Logic/Math Errors** | High | ⏸️ **Deferred** | Reasoning Model (V6) |
| **Missed Details** | Medium | 🚀 **Next Up** | CrossEncoder Re-ranker |
| **Vague Queries** | Low | ℹ️ Medium | Query Expansion |
