# Running and testing

Run commands from the repository root. Scripts resolve their working directory themselves, but the manual Python commands below assume that location.

## Startup order

1. Start Docker Desktop and Ollama. Check `docker ps` before starting any new containers.
2. On a fresh machine, start the [supporting Compose project](../docker/README.md). Existing services can be reused.
3. Run `.\.venv\Scripts\python.exe scripts/doctor.py --require-model`. It checks core packages and the exact Ollama model tag without opening Qdrant. Supporting-service failures are reported; `--require-model` exits nonzero for missing Python/model prerequisites.
4. If this is a new collection, run `.\scripts\seed.ps1` with API stopped. It creates the collection once and preserves existing data on repeat runs.
5. Run `.\scripts\start.ps1 -OpenBrowser`. Add `-DockerServices` to start missing supporting services using the template. The script reuses an already healthy API on 8003 and never intentionally starts a second Uvicorn there.
6. [Import/configure/publish n8n](N8N_INTEGRATION.md). Do not duplicate an active webhook path.

The detached API writes ignored `.runtime/api.*.log` files and a PID/start-time record. To use a foreground server with graceful Ctrl+C shutdown instead:

```powershell
.\.venv\Scripts\python.exe -m uvicorn api:app --host 0.0.0.0 --port 8003
```

Use one API worker per embedded Qdrant directory. Binding to all interfaces is needed for Docker-to-host access, and requires appropriate Windows Firewall restrictions.

## Health and warm-up

```powershell
Invoke-RestMethod http://localhost:8003/healthz
Invoke-RestMethod http://localhost:8003/api/status
.\scripts\test_api.ps1 -Message 'What is included in routine AC maintenance?'
```

Health reports the process/configuration, not model readiness. Status checks collection existence, not document count or Ollama availability. The first real process/classify request loads Laya; the first embedding loads MiniLM. A direct maintenance request warms the inference path before automation. Direct mode does not send email.

## End-to-end automation and SMTP

```powershell
.\scripts\test_webhook.ps1 -Message 'What is included in routine AC maintenance?'
.\scripts\test_mailpit.ps1
```

The webhook script reads `N8N_WEBHOOK_URL` from the same settings as FastAPI. The SMTP check creates a unique fictional request ID, calls `/api/notify`, and verifies that subject in Mailpit's latest messages. It verifies delivery independently of RAG.

Open <http://localhost:8003>, enter `WORKFLOW_TOKEN`, leave full-workflow mode selected, and submit the question. Expect a result, source filenames, decision/retrieval diagnostics, an n8n execution, and a Mailpit message. The [walkthrough](DEMO_WALKTHROUGH.md) and [evidence files](evidence/maintenance.json) show actual observed behavior. Do not assume all questions will produce an answer.

For test URLs, open the Webhook node, select **Listen for test event**, then run `test_webhook.ps1 -TestMode`. The one-shot test listener is different from a published production webhook.

## Automated verification without models

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check api.py app.py cli.py service scripts tests
.\.venv\Scripts\python.exe scripts/validate_repo.py
docker compose -f docker/compose.yaml config --quiet
```

The suite covers policy branches, authentication, request validation, Laya response handling with fakes, SMTP deduplication, Qdrant lifecycle, non-destructive seeding, and real embedded Qdrant persistence with a tiny fake encoder. No Qwen/Laya/MiniLM weights are required for these tests. `requirements-ci.txt` installs only the dependencies needed for this path; GitHub Actions runs it on Python 3.12.

Live inference, webhook operation, emails, screenshots, and fresh Compose startup are separate checks. See [VALIDATION.md](VALIDATION.md) for their exact results; unit tests do not prove live model accuracy.

## Safe shutdown

```powershell
.\scripts\stop.ps1
# Only for containers owned by the new template project:
.\scripts\stop.ps1 -DockerServices
```

The API stop script acts only on a matching PID/start-time and command line recorded by this checkout. It leaves manually started/existing APIs alone. A private local shutdown signal asks the owned Uvicorn server to drain requests and run lifespan cleanup, including closing Qdrant. The script waits up to 45 seconds and refuses to force termination on timeout. Foreground Uvicorn can also be stopped with Ctrl+C. Never delete lock/database files while a process is alive. `-DockerServices` uses Compose `stop`, retains volumes, and does not stop the older FieldFlow Compose project or Ollama.
