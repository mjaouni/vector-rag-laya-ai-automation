# Recorded end-to-end demonstration

Tested on **26 October 2026, Asia/Beirut**. JSON evidence uses UTC timestamps, so its calendar date can be 25 October. These are actual model/service results, not fabricated example successes.

## Two validation contexts

The original running installation used FastAPI 8003, n8n 5678, Mailpit 8025/1025, and the existing indexed database. Five synthetic scenarios ran there without replacing containers or their workflows. Their evidence files use the short scenario names below.

The consolidated code was then started separately on FastAPI **8004**, with a newly seeded Qdrant directory and separate notification ledger. The fresh Compose template was instantiated as an isolated validation project with n8n **15678**, Mailpit UI **18025**, and SMTP **11025**. Its sanitized workflow was imported, a local Header Auth credential selected, URLs adjusted to 8004, and publication verified. Ollama remained the existing Windows instance at 11434. The default setup instructions continue to use 8003/5678/8025/1025.

Screenshots come from this isolated validation context. They show real application/n8n/Mailpit interfaces and real executions with the same project code and model settings. No user authentication or original workflow was overwritten. The test-instance provisioning helpers and session credentials are private runtime files, not a supported installation feature.

## Routine AC maintenance

Question: **What is included in routine AC maintenance?**

1. The [browser home](screenshots/application-home.png) is served by the consolidated FastAPI process. The local token is entered only for submission and cleared before capture.
2. The browser sends `/api/via-n8n`; the configured production webhook receives it. The [workflow canvas](screenshots/n8n-workflow.png) and [webhook settings](screenshots/n8n-webhook.png) show the actual routing and intake configuration.
3. n8n's Process AI node calls `/api/process` through Docker's host route with Header Auth.
4. Laya returns provider `laya-local`, intent `maintenance`, confidence **0.6997**, hazard probability **0.0598**, and human probability **0.0951**. No review flag is set. These are model outputs, not accuracy guarantees.
5. MiniLM/Qdrant retrieves `maintenance.md` at cosine score **0.6100**, followed by `safety.md` **0.3578**, `pricing.md` **0.3231**, and `appointments.md` **0.3221**. The [diagnostics](screenshots/application-diagnostics.png) and [scrolled passage payload](screenshots/application-sources.png) expose the actual returned data.
6. Ollama/Qwen produces a short answer about filters, professional inspection, thermostat settings, and airflow. FastAPI returns `status: answered` and `reason: grounded_response`.
7. The [answer screen](screenshots/application-answer.png) shows the result. The exact matching response and SMTP text are in [consolidated maintenance evidence](evidence/consolidated-maintenance.json), request ID `a05bcae3-3cbe-43b6-af7b-548ff0fa9430`.
8. n8n selects the false/answer branch and calls `/api/notify`. The successful execution and notification result are captured in the [screenshot index](screenshots/README.md).
9. Mailpit receives the message. Its [inbox](screenshots/mailpit-inbox.png) and [opened email](screenshots/mailpit-email.png) show the same request ID, status, answer, and source list.

### Observed citation limitation

The actual answer cites **`[source.md]`**, which is not one of the retrieved filenames. The separate `sources` array correctly lists retrieved documents. This is an observed citation-format failure in a run whose pipeline status is `answered`; it has not been edited out of evidence or screenshots. The current system requests filename citations but does not validate them independently. `grounded_response` must not be read as a claim-level verification result.

The first cold consolidated execution took roughly 143 seconds according to n8n, including model loading. Subsequent model-warm runs were faster; this is not a performance benchmark. The Laya runtime also warned about fallback temperature metadata for its `choice:11+` setting. Current questions use six intent choices; no calibration study was performed for these demo thresholds.

## Scenario results

| Scenario | Intended outcome | Actual verification |
|---|---|---|
| Routine maintenance | Answer via RAG and send answer email | **Live tested in both contexts**: answered, Laya maintenance, Qdrant hits, Ollama output, Mailpit receipt. Invalid citation noted above. [Original evidence](evidence/maintenance.json), [consolidated evidence](evidence/consolidated-maintenance.json). |
| Service area: `Do you serve ZIP 90210?` | Answer using retrieved policy | **Live tested, expected answer not achieved**: `needs_review`, `human_or_booking_request`; Mailpit received review notification. This is over-escalation, not a successful service-area answer. [Evidence](evidence/service-area.json). |
| Book tomorrow morning | Human review, no booking | **Live tested**: `needs_review`, `human_or_booking_request`, Mailpit review notification, no booking action. [Evidence](evidence/booking.json). |
| Gas odor | Safety escalation, skip generation | **Live tested in both contexts**: `needs_review`, `potential_hazard`, no sources, Mailpit review notification. [Original](evidence/hazard.json), [consolidated](evidence/consolidated-hazard.json), [email](screenshots/mailpit-review.png). |
| Unknown compressor serial number | Controlled review/unanswered result | **Live tested**: `needs_review`, `uncertain_classification`, Mailpit notification. [Evidence](evidence/missing-information.json). Empty-retrieval behavior is separately unit tested. |
| Model failure | Controlled review | **Offline fault-injection tested** for Laya import failure and generation timeout. No live service was intentionally broken; live outage email behavior is not verified. |

The [summary JSON](evidence/summary.json) records the five original-installation runs. The [validation report](VALIDATION.md) separates live checks from automated unit checks and remaining gaps.
