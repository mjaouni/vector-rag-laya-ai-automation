# Validation report

Validated on **26 October 2026, Asia/Beirut**, with Python 3.12.2 on Windows. [Tested package versions](TESTED_VERSIONS.md), [request evidence](evidence/summary.json), and [screenshot provenance](screenshots/README.md) are part of the repository.

## Automated and repository checks

| Check | Result |
|---|---|
| Original test suite | 15 passed before consolidation |
| Final offline suite | **24 passed**; last local run completed in 5.25 seconds |
| Ruff (`F`, `E9`) | Passed for application, service, scripts, tests |
| Python syntax, YAML, relative Markdown links | Passed through `scripts/validate_repo.py` |
| PowerShell syntax/compatibility | All `.ps1` files parsed with PowerShell's AST parser; configuration helper and new-token expression tested under Windows PowerShell 5.1 after fixing native-argument quoting |
| Workflow JSON | Valid seven-node graph, inactive public import, three Header Auth HTTP nodes, no embedded credential values or local credential IDs |
| Compose syntax | `docker compose -f docker/compose.yaml config --quiet` passed |
| Publication hygiene | `scripts/check_publication.py` checked credential/key patterns, actual non-placeholder token values, personal paths, non-demo email addresses, runtime paths, model extensions, and large files; no findings |
| Screenshots | All 11 actual captures visually inspected; token cleared, no private account data or unrelated inbox contents |

The final commit is also reviewed with indexed-content checks and the history scan before push. The initial source folder had no Git history to import. Commit authors use a GitHub noreply address rather than the configured private/business email.

## Runtime and integration checks

| Check | Result and scope |
|---|---|
| Existing API health/status | Healthy on 8003; original collection indexed; Laya/Qwen2.5:7b configured |
| Existing services | n8n 2.44.4 and Mailpit runtime 1.31.6 inspected without recreation; published loopback ports confirmed |
| Ollama | API reachable; exact `qwen2.5:7b` tag installed; real answer generation exercised |
| Fresh Compose startup | Both pinned images started successfully under isolated project name and alternate host ports; persistent volumes/network created |
| Real MiniLM ingestion | Separate validation directory seeded: **7 documents / 7 chunks** |
| Repeat ingestion | Existing collection skipped; no delete/rebuild operation |
| Consolidated API startup | `scripts/start.ps1 -Port 8004` started the final code with isolated storage/SMTP/webhook settings |
| Duplicate process guard | Default startup reused the existing healthy 8003 API; no duplicate started |
| Seed/process guard | `scripts/seed.ps1` refused while port 8003 was active |
| Workflow import | Public sanitized export imported into fresh isolated n8n; Header Auth credential assigned; workflow published successfully |
| Maintenance full workflow | Real browser → consolidated FastAPI → n8n → Laya/MiniLM/Qdrant/Ollama → SMTP → Mailpit → browser; `answered`, `grounded_response` |
| Review full workflow | Real gas-odor request through consolidated stack; `needs_review`, `potential_hazard`; Mailpit review receipt verified |
| Notification node | Real n8n output: `notified:true`, `deduplicated:false`, matching request ID |
| SMTP test helper | `scripts/test_mailpit.ps1` created a unique synthetic notification and verified its subject in the original local inbox |
| Graceful owned shutdown | Process identity/start time verified; local signal initiated Uvicorn shutdown; log confirmed application shutdown complete; Qdrant reopened afterward |
| Cleanup | Validation API stopped; temporary Compose containers stopped with volumes retained; temporary inspection export removed; original 8003 API and original two containers remained running |

The isolated validation topology used API 8004, n8n 15678, Mailpit UI 18025, SMTP 11025, and the existing Ollama 11434. This avoided default-port collisions or modification of the established database. Normal fresh-install defaults remain 8003/5678/8025/1025.

## Actual scenario outcomes and gaps

See [the walkthrough](DEMO_WALKTHROUGH.md) for inputs and exact evidence. Maintenance, booking, hazard, missing-information, and service-area requests all produced completed original-workflow executions with Mailpit notifications. Maintenance and hazard were additionally verified using the consolidated code and sanitized workflow in the isolated stack.

Two behavior limitations were observed and preserved in the evidence:

- Service-area policy question over-escalated to review; the expected policy answer was **not** achieved.
- The maintenance answer used the invalid citation `[source.md]` although the separately returned source list was correct. Citation/claim validation is **not** implemented.

Model failure behavior was verified through offline fault injection, not by stopping live model services. Empty-retrieval review is unit tested; the live unknown-information question took the uncertain-classification branch. Optional Streamlit was inspected but not launched during this validation. A complete clean-machine Python/model download installation was not repeated; the existing Python environment and cached models were used. Fresh supporting-service startup, sanitized workflow import, real MiniLM seeding, and final-code end-to-end execution were tested independently.

The Laya runtime emitted a fallback-temperature warning for its `choice:11+` metadata; no probability-calibration study was performed. No exhaustive vulnerability audit, model-accuracy evaluation, or production security certification is claimed.

## CI and publication

The [GitHub Actions workflow](../.github/workflows/ci.yml) installs `requirements-ci.txt` on Python 3.12 and runs Ruff, pytest, repository/link/workflow checks, publication checks, and Compose validation without AI weights or live services. Remote run status is available on the repository's Actions page after a push and is checked as part of publication verification.

The owner chose publication without a license for now; no application license grant has been added. See [licensing](LICENSING.md). The repository contains integration code, configuration templates, fictional knowledge documents, and screenshots—not third-party application source, private databases, credentials, or model binaries.
