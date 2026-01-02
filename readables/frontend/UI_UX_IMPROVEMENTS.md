# Frontend UI/UX Improvement Plan

## Overview
This document outlines advanced features and improvements for the DocuMind AI frontend (`templates/index.html`) to elevate it from a simple chat interface to a professional Document Intelligence Dashboard.

## 🚀 Priority 1: Core Experience (High Impact)

### 1. Markdown & Code Rendering
-   **Concept**: Convert raw text responses into rich HTML.
-   **Features**:
    -   Render tables properly (e.g., financial comparisons).
    -   Syntax highlighting for code blocks (Python, JSON, SQL).
    -   Render lists, bold, italics, and headers.
-   **Tech**: `marked.js` + `highlight.js`.

### 2. Live File Explorer Sidebar
-   **Concept**: Visual navigation of the `data/sorted` directory.
-   **Features**:
    -   Collapsible sidebar on the left.
    -   Tree view of Domains -> Categories -> Files.
    -   "Eye" icon to preview file contents immediately.
    -   Context menu to Delete or Re-classify files manually.

### 3. Drag-and-Drop "Dropzone"
-   **Concept**: Visual feedback for file ingestion.
-   **Features**:
    -   Large drop area overlay when dragging files.
    -   **Live Progress Bar**: "Uploading" -> "Processing" -> "Classifying" -> "Done".
    -   Immediate notification of where the file went (e.g., "Moved to: Finance > Tax").

## 🎨 Priority 2: Interaction & Visuals

### 4. Knowledge Graph Visualization
-   **Concept**: Interactive node graph showing how documents relate.
-   **Features**:
    -   Visual nodes for Domains (Technology, Legal).
    -   Lines connecting related documents (based on vector similarity).
    -   Click a node to filter chat context to that specific domain.
-   **Tech**: `d3.js` or `vis.js`.

### 5. Split-Screen Document Preview
-   **Concept**: See the source evidence side-by-side with the chat.
-   **Features**:
    -   When a citation `[Source 1]` is clicked, slide out a panel on the right.
    -   Highlight the exact text chunk used by the AI.
    -   PDF viewer integration for full page context.

### 6. Voice Command Center (Speech-to-Text)
-   **Concept**: Hands-free operation.
-   **Features**:
    -   Microphone button in the input bar.
    -   Real-time transcription of user voice to text.
    -   "Wake words" or voice commands (e.g., "Clear history", "Read that again").

## 🛠️ Priority 3: Utility & Power Tools

### 7. Prompt Library / Quick Starters
-   **Concept**: Domain-aware quick actions.
-   **Features**:
    -   If user is viewing "Legal" folder, show chips: "Summarize Liability", "Find Expiry Dates".
    -   If viewing "Code", show: "Explain Architecture", "Find Bugs".

### 8. System Status Dashboard
-   **Concept**: detailed health check panel.
-   **Features**:
    -   Real-time RAM usage of Ollama.
    -   Vector DB stats (Total Chunks, Index size).
    -   "Classified Count" ticker (e.g., "Processed 500 files today").

### 9. Smart Search & filtering
-   **Concept**: "Chat with THIS file only".
-   **Features**:
    -   Dropdown next to input: "Search in: All / Legal / Only current file".
    -   Date filters ("Only answer from documents added last week").

## Implementation Roadmap (Recommended Order)
1.  **Markdown Support** (Easy win, huge readability boost).
2.  **Sidebar Explorer** (Crucial for the "Autonomous Sorting" value proposition).
3.  **Doc Preview** (Critical for trust/verification).
4.  **Graph Viz** (The "Wow" factor).
