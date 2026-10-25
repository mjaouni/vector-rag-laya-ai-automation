# Request lifecycle

```mermaid
sequenceDiagram
    actor User
    participant UI as Browser
    participant API as FastAPI
    participant N as n8n
    participant L as Laya
    participant Q as MiniLM + Qdrant
    participant O as Ollama/Qwen
    participant M as Mailpit
    User->>UI: Routine AC maintenance question
    UI->>API: POST /api/via-n8n + X-Demo-Token
    API->>N: POST /webhook/rag-laya-intake
    N->>API: POST /api/process + Header Auth
    API->>L: Structured intent, hazard, human questions
    L-->>API: Typed scores and intent
    alt Hazard
        API-->>N: needs_review, potential_hazard
    else Retrieval permitted
        API->>Q: Embed question and search cosine neighbors
        Q-->>API: Sources, scores, passages
        alt Sufficient evidence and no review flag
            API->>O: Question + passages + system policy
            O-->>API: Answer with requested filename citations
            API-->>N: answered, grounded_response
        else Booking, uncertainty, missing evidence, or failure
            API-->>N: needs_review with reason
        end
    end
    N->>N: Choose review or answer branch
    N->>API: POST /api/notify with original result
    API->>API: Validate request ID; check SQLite dedup
    API->>M: SMTP notification if not already sent
    API-->>N: Notification outcome
    N-->>API: Original Process AI result
    API-->>UI: JSON response
    UI-->>User: Answer, sources, diagnostic details
```

1. The UI collects a fictional customer message and shared local token. All user-provided text is displayed using `textContent`, not HTML interpolation.
2. FastAPI validates message length and optional request ID. The n8n proxy uses a fixed configured URL rather than a URL supplied in the request.
3. `/api/process` assigns a UUID if none was supplied and invokes Laya. Model import/inference failure returns a controlled `needs_review` response with provider `unavailable`.
4. Hazards return immediately before retrieval/generation. Other requests retrieve passages; a retrieval failure or empty result returns review.
5. Booking/human flags and uncertainty return review before generation. No branch calls a booking tool or real customer messaging service.
6. Permitted requests call Ollama with the selected passages. Empty output, HTTP errors, and timeouts return controlled review. Successful text is labeled `grounded_response`, which describes the attempted RAG path; it is not proof that each claim was independently verified.
7. n8n routes by `status`. Both notification nodes call Python `/api/notify`, then the corresponding response node returns the original AI result, preserving sources and decision details.
8. Mailpit captures test SMTP messages locally. The notification records request ID, status, reason, answer, and sources. Replaying a successful request ID does not normally resend an email.

Limits/timeouts: API-to-n8n 180 seconds; n8n HTTP nodes 180 seconds; Ollama 120 seconds; SMTP 10 seconds. Cold model downloads can exceed these limits. Warm models with a direct API request before the full workflow. HTTP timeout cancellation does not guarantee cancellation of a running synchronous inference.
