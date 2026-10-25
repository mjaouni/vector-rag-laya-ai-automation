from dataclasses import dataclass
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")


def local_path(name: str, default: str) -> Path:
    path = Path(os.getenv(name, default)).expanduser()
    return path if path.is_absolute() else ROOT / path


@dataclass(frozen=True)
class Settings:
    data_dir: Path = local_path("QDRANT_PATH", "data/qdrant")
    docs_dir: Path = local_path("DOCS_DIR", "sample_docs")
    notification_db: Path = local_path("NOTIFICATION_DB", "data/notifications.sqlite3")
    collection: str = os.getenv("QDRANT_COLLECTION", "hvac_kb_minilm_v1")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    ollama_url: str = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
    decision_provider: str = os.getenv("DECISION_PROVIDER", "laya").lower()
    min_relevance: float = float(os.getenv("MIN_RELEVANCE", "0.20"))
    top_k: int = max(1, min(10, int(os.getenv("TOP_K", "4"))))
    smtp_host: str = os.getenv("SMTP_HOST", "127.0.0.1")
    smtp_port: int = int(os.getenv("SMTP_PORT", "1025"))
    mail_from: str = os.getenv("MAIL_FROM", "rag-demo@example.test")
    mail_to: str = os.getenv("MAIL_TO", "reviewer@example.test")
    workflow_token: str = os.getenv("WORKFLOW_TOKEN", "local-dev-only-change-me")
    n8n_webhook_url: str = os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook/rag-laya-intake")


settings = Settings()
