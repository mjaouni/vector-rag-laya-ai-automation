# Troubleshooting

Start with `.\.venv\Scripts\python.exe scripts/doctor.py`, `docker ps`, API logs, and the failing n8n execution node. Health does not prove model readiness.

| Symptom | Check and resolution |
|---|---|
| Qdrant collection missing | Stop API, run `scripts/seed.ps1`, then restart. Check collection/path in `.env`. |
| Qdrant locked / already accessed | Use one API worker and one process per storage directory. Stop the owner gracefully before seeding. Do not remove a live lock file or delete the database. |
| Changed documents are not reflected | Seed intentionally skips existing collections. With API stopped, choose a new `QDRANT_COLLECTION` and seed it; retain the old collection. |
| Vector dimension mismatch | Changing `EMBEDDING_MODEL` requires a new collection. Do not query an old collection with a different embedding dimension. |
| `QdrantClient.__del__`, `sys.meta_path is None` on shutdown | Explicit close in CLI `finally` and FastAPI lifespan addresses interpreter-teardown warnings. A successful seed dictionary can precede warnings in older versions. Use the owned-process stop script or foreground Ctrl+C for graceful shutdown. |
| Port 8003 occupied | `Get-NetTCPConnection -State Listen -LocalPort 8003`; inspect PID. Startup reuses a healthy project API and refuses a foreign service. Stop the correct existing process; do not start duplicates. |
| n8n webhook 404 | Publish the workflow for `/webhook/`; for `/webhook-test/`, actively listen for a test event. Confirm path and POST method. |
| n8n HTTP node connection refused | Use `host.docker.internal:8003`, listen on `0.0.0.0`, and check Windows Firewall. `localhost` inside the container is not Windows. |
| Protected API 401 | Match `.env`/environment `WORKFLOW_TOKEN`, UI entry, and Header Auth credential selected in all three HTTP nodes. Restart API after config changes. |
| Workflow imported but missing credential | Select/create the Header Auth credential; public exports intentionally contain no local ID/token. |
| Mailpit UI works but SMTP fails | Verify host port 1025 is published. Match `SMTP_PORT` to host mapping; SMTP client runs on Windows, not n8n. |
| Answer generated, webhook failed | Inspect notification node; SMTP failure stops the response branch. This release has no asynchronous notification queue. |
| No new email on replay | The same request ID is deduplicated after successful send. Use a new ID for a new logical test; do not delete the ledger. |
| Ollama model not found | `ollama list`; pull `qwen2.5:7b` or configure the exact installed tag and restart. A different 0.5b tag is not the default demo model. |
| Laya import/checkpoint failure | Install `requirements-laya.txt` into the same Python 3.12 venv. Check checkpoint download/network/cache permissions and available RAM. Rules mode is explicitly diagnostic and does not verify Laya. |
| Slow first response/timeouts | Initial Torch imports/checkpoint downloads/model loads are expensive. Warm with direct `test_api.ps1`, then retry n8n. Avoid concurrent cold requests. |
| Unexpected review for service area | Decision scores are probabilistic; inspect `human_flag`, `booking_flag`, confidence, and `routing_model`. The recorded service-area test over-escalated. Do not silently weaken safety thresholds to force a demo answer. |
| Unrelated question receives a plausible answer | Similarity cutoff is not an entailment test. Inspect passages and cited claims; there is no independent citation/claim verifier. |
| PowerShell script policy error | Run the individual file with a process-scoped `-ExecutionPolicy Bypass`, or follow equivalent manual commands. No persistent security setting change is needed. |
| GitHub CI fails before models | CI is offline/mocked. Inspect dependency, syntax, lint, link, and workflow-validation output; model downloads are not required. |

If a response is `needs_review`, read its `reason`: that is often intended safe behavior, not a broken HTTP endpoint. No response constitutes a real booking, dispatch, emergency intervention, or customer email.
