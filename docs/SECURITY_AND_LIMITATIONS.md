# Security and limitations

This is a trusted-local-development proof of concept using fictional HVAC data. It is not an emergency system, production service, real business, appointment backend, or customer communications platform.

## Boundaries implemented

- Protected FastAPI POST routes compare a shared `X-Demo-Token` using `hmac.compare_digest`.
- Fixed server-side n8n URL and SMTP recipient prevent request input from choosing arbitrary proxy destinations or email recipients.
- Query message length and request-ID shape are validated; notification IDs/statuses are validated before SMTP.
- Hazards, booking requests, human requests, uncertainty, missing evidence, and model failures route to review. Hazard routing skips retrieval/generation; booking routing does not call an action tool.
- Public workflow JSON contains no credentials, token values, local instance IDs, or execution/pinned data. Header Auth stores the local token separately in n8n.
- Compose publishes n8n/Mailpit only on loopback and retains private state in volumes. Real `.env`, caches, model binaries, databases, runtime logs, and private exports are ignored by Git.
- The browser renders results as text. Prompt instructions treat retrieved material as untrusted reference text.

## Boundaries not implemented

The n8n intake webhook, browser home, health/status, generated API docs, and Mailpit UI are unauthenticated. The shared API token is not per-user identity or least-privilege authorization. A compromised token permits process/classify/retrieve/notify/proxy access. The example value is public; setup generates a random value for a fresh `.env`, while existing environments are preserved. The existing live demo may still use its older example token; rotate it deliberately before expanding access.

There is no HTTPS termination, intake rate limiting, CSRF/session design, abuse detection, durable queue, centralized audit system, tenant isolation, secret manager, or distributed notification transaction. Do not expose the local webhook publicly. FastAPI's `0.0.0.0` bind is reachable beyond loopback unless restricted by the host firewall; only use a trusted development network.

Prompt injection is reduced by prompt structure, not eliminated. Documents/questions may influence generation. Filename citations are requested by the prompt; there is no independent filename whitelist enforcement, claim-to-passage verification, or answer entailment check. `grounded_response` means the RAG path ran, not that every assertion is proven. A similarity score is not a factual confidence probability. A low threshold can admit irrelevant passages; irrelevant hits can still reach generation.

Laya's probabilities and intent estimates are not permissions. Thresholds are hand-set demo policy, not measured for an operational HVAC deployment. English keyword safeguards are incomplete, false positives can over-escalate, and multilingual safety recall is not evaluated. The recorded service-area run demonstrates over-escalation. Missing/invalid scores require review in the consolidated code. Model-generated answers still need human assessment.

Embedded Qdrant supports one process per directory. Seed creates missing collections and does not refresh existing ones. Document/model changes require a new collection. There are no migrations, backup automation, index ownership metadata, corpus provenance signatures, or access controls for documents.

SQLite notification deduplication can suppress a changed request that reuses an ID. SMTP send and database commit are separate, so a crash can duplicate a notification on replay. An email is only a test notification, and `needs_review` does not prove a person has received or acted on it. No action confirms an appointment or dispatches help.

## Publication review

Before publication, review `git diff --cached`, tracked filenames, large files, credential patterns, email addresses, personal paths, and every screenshot. `scripts/validate_repo.py` checks structure, size, links, and runtime-file exclusions. `scripts/check_publication.py --staged` scans indexed content for credential/private-key patterns, personal paths, non-demo email addresses, model files, and the actual non-placeholder local token without printing matches. Run it with `--history` after committing to inspect reachable commit file versions. These are conservative checks, not an exhaustive secrets or vulnerability audit; screenshots require visual review. Model and third-party licenses remain independent; see [licensing](LICENSING.md).

## Practical next steps

Add authenticated/rate-limited intake, separate service identities, HTTPS, independent citation and entailment checks, a measured decision/abstention evaluation set, durable notification retries, request-ID ownership, and a real human approval system before any external deployment. Move to server-based Qdrant and managed worker execution only when concurrency requirements justify the extra deployment complexity.
