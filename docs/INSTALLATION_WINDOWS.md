# Windows installation

Use Python 3.12 **64-bit**, PowerShell, Git, Docker Desktop with Linux containers, and Ollama for Windows. Obtain software from its official distribution. This project requires no paid inference API. Initial pip/model/image downloads require internet; cached model inference can run locally afterward.

Plan for several GB for Qwen2.5:7b (about 4.7 GB in the investigated installation), additional Torch/Laya/MiniLM downloads, and sufficient RAM for all three models plus Windows. No fixed minimum RAM has been benchmarked for this project. CPU works but can be slow; GPU support is optional and depends on your installed runtime.

## Clone and install

```powershell
git clone https://github.com/mjaouni/vector-rag-laya-ai-automation.git
cd vector-rag-laya-ai-automation
.\scripts\setup.ps1
```

The script creates `.venv` if absent, installs base/test/Laya dependencies, and copies `.env.example` only when `.env` does not exist. A new environment gets a random local token. Existing configuration is retained. Optional UI: `setup.ps1 -WithUI`. `-SkipLaya` omits the Laya install; if using that diagnostic option, explicitly set `DECISION_PROVIDER=rules` and do not describe the result as Laya inference.

If script execution is restricted, run an individual script with `powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1`, or execute its commands manually. No persistent execution-policy change is needed.

Manual equivalent:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-laya.txt -r requirements-dev.txt
Copy-Item .env.example .env  # only if .env does not already exist
```

With manual installation, replace the public example token with a unique local value. Do not paste it into screenshots or commit it. In the browser, enter the local token into its password field. An environment variable set in your shell takes precedence over the `.env` file.

## Configure the actual settings

All application configuration comes through `service/config.py` and [`.env.example`](../.env.example). Restart FastAPI after changes.

| Variable | Default | Meaning |
|---|---|---|
| `OLLAMA_URL` | `http://127.0.0.1:11434` | Windows Ollama base URL |
| `OLLAMA_MODEL` | `qwen2.5:7b` | Exact tag shown by `ollama list` |
| `DECISION_PROVIDER` | `laya` | `laya` for real inference, `rules` for explicitly labeled plumbing checks |
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | SentenceTransformer model ID/path |
| `QDRANT_COLLECTION` | `hvac_kb_minilm_v1` | Dedicated knowledge collection |
| `QDRANT_PATH` | `data/qdrant` | Embedded database directory |
| `DOCS_DIR` | `sample_docs` | Markdown corpus directory |
| `NOTIFICATION_DB` | `data/notifications.sqlite3` | SMTP deduplication database |
| `MIN_RELEVANCE` | `0.20` | Minimum retained cosine score; not a calibrated probability |
| `TOP_K` | `4` | Search limit, clamped to 1–10 |
| `SMTP_HOST` | `127.0.0.1` | Mailpit host reachable from Windows |
| `SMTP_PORT` | `1025` | Published host SMTP port |
| `MAIL_FROM` | `rag-demo@example.test` | Fictional sender |
| `MAIL_TO` | `reviewer@example.test` | Local operator test recipient |
| `N8N_WEBHOOK_URL` | `http://localhost:5678/webhook/rag-laya-intake` | Fixed full-workflow destination |
| `WORKFLOW_TOKEN` | public example in template | Shared token for protected FastAPI endpoints |

The three path settings resolve relative paths against the repository root, independent of the shell directory. Do not reuse a collection with a different embedding model/dimension. Choose a new collection name and seed with the API stopped.

## Start dependencies

Start Docker Desktop. First inspect `docker ps`: existing n8n/Mailpit on the default ports can be reused. On a fresh installation only:

```powershell
docker compose -f docker/compose.yaml config --quiet
docker compose -f docker/compose.yaml up -d
```

Start Ollama through its normal Windows application/service, then:

```powershell
ollama pull qwen2.5:7b
ollama list
Invoke-RestMethod http://localhost:11434/api/tags
.\.venv\Scripts\python.exe scripts/doctor.py --require-model
```

Laya is installed from `requirements-laya.txt` and downloads its own checkpoint on first prediction. Do not try `ollama pull laya`. MiniLM downloads when embedding is first required. The doctor checks package availability and Ollama tags; it does not download or execute Laya.

## Initialize, start, and connect automation

```powershell
.\scripts\seed.ps1
.\scripts\start.ps1 -OpenBrowser
```

Seed before starting the API. A dictionary with `documents`, `chunks`, and `collection` indicates initialization; an existing collection returns `skipped: True`. Never seed against an embedded store opened by another process. The wrapper refuses while port 8003 is active, and Qdrant's own file lock protects against other owners.

Open n8n and finish local account setup if this is a fresh instance. Follow [workflow import and Header Auth setup](N8N_INTEGRATION.md), publish it, then run [the end-to-end checks](RUNNING_AND_TESTING.md). No automatic workflow/credential provisioning is claimed.

For the optional Streamlit UI:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-ui.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

External installation references: [Laya model card](https://huggingface.co/convaiinnovations/laya), [Ollama API](https://docs.ollama.com/api), [Qdrant client](https://github.com/qdrant/qdrant-client), and [Mailpit Docker](https://mailpit.axllent.org/docs/install/docker/).
