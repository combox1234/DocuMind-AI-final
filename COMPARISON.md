# Version Comparison

| Feature | V1 (MVP) | V2 (Production) | V3 (UI/UX) | V4 (Stability) | V5 (Dual LLM) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **LLM Strategy** | None (Keywords) | Single LLM | Single LLM | Single LLM | **Dual (Classify + Chat)** |
| **Authentication** | ❌ | ❌ | ❌ | ❌ | **✅ JWT** |
| **Classification** | Basic | Advanced | Advanced | Advanced | **Hierarchy + LLM** |
| **UI** | HTML Raw | Basic | Pro (Themes) | Glassnorphism | **Refined** |
| **Security** | None | None | None | None | **Token Based** |
| **Scalability** | Low | Medium | Medium | Medium | **High** |

## Key Upgrades in V5
1.  **Dual LLM**: Decoupled ingestion (Llama 3.2 1B) from logic (Llama 3.1 8B).
2.  **JWT Auth**: `flask-jwt-extended` added for API security.
3.  **Strict Mode**: System prompt refined to prevent hallucinations.
