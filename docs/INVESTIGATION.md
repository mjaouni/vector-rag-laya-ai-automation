# Repository investigation

Investigated 25–26 October 2026 before consolidation. The supplied folder had no `.git` directory, remote, branch, license, Compose file, CI, or separate documentation directory. It contained one application, seven fictional Markdown knowledge documents, an existing `.venv`, private `.env`, embedded Qdrant data, and 15 passing tests. Generated files are excluded from publication.

## Existing implementation retained

| Component | Entry point / responsibility |
|---|---|
| FastAPI | `api.py`; browser UI, health, processing, classification, retrieval, notification, n8n proxy |
| Browser | `web.html`; same-origin API requests, diagnostic JSON |
| Optional Streamlit | `app.py`; requests the same backend |
| Configuration | `service/config.py`; environment overrides `.env`, repository-relative paths |
| Decision | `service/decisions.py`; cached Laya Router, keyword safeguards, explicit rules diagnostic mode |
| Retrieval | `service/retrieval.py`; MiniLM, character chunks, embedded Qdrant, cosine scores |
| Generation | `service/generation.py`; Ollama `/api/chat`, Qwen2.5:7b |
| Policy pipeline | `service/pipeline.py`; review routing, retrieval, generation, failure handling |
| Notification | `service/notify.py`; operator SMTP email, SQLite request-ID deduplication |
| CLI | `cli.py seed`; collection initialization and explicit client close |
| Automation | `n8n/rag-laya-mailpit.json`; seven-node workflow |

The existing `data/qdrant` collection was indexed. The API was already serving port 8003 with `DECISION_PROVIDER=laya` and `OLLAMA_MODEL=qwen2.5:7b`. Ollama also held a 0.5b model, which is not the model configured for this application.

## Existing Docker environment

| Container | Observed image | Published host ports | Persistence |
|---|---|---|---|
| `fieldflow-n8n-demo-n8n-1` | `n8nio/n8n:2.44.4` | loopback 5678 | named volume at `/home/node/.n8n` |
| `fieldflow-n8n-demo-mailpit-1` | `axllent/mailpit:latest`, runtime v1.31.6 | loopback 8025 and 1025 | named volume at `/data` |

Both containers use the existing `fieldflow-n8n-demo_default` network. The RAG workflow is active; its nodes, URLs, and branch connections match the source export. Other FieldFlow workflows share that n8n installation and are unrelated. Their source, credentials, databases, and exports are not included. Neither existing container was recreated or removed.

The new Compose project uses its own name, network, and volumes. It is a fresh-install template, not a migration of these volumes. The Mailpit tag is pinned to the observed runtime version rather than `latest`.

## Changes justified by investigation

- Preserved canonical application paths and the seven-node workflow; no duplicate implementation.
- Removed fixed authentication headers and instance metadata from the public workflow; select a Header Auth credential after import.
- Changed seed from delete/recreate to create-if-absent. Existing collections are retained; use a new collection name when indexing changed documents or embeddings.
- Added optional repository-relative data/document/database settings for isolated validation.
- Replaced the startup helper that could launch duplicate servers with port checks, readiness checks, and owned PID tracking.
- Test scripts now read the same Python settings as the backend.
- Missing or invalid Laya confidence now requires review, matching the existing fail-closed intent.
- Kept local `.env`, virtual environment, caches, model weights, logs, notifications, and vector data out of Git.

See [validation](VALIDATION.md) for observed results and [security limitations](SECURITY_AND_LIMITATIONS.md) for operational boundaries.
