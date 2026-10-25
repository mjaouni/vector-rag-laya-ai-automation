import json
from pathlib import Path

def test_importable_workflow_structure():
    path=Path(__file__).resolve().parents[1] / "n8n" / "rag-laya-mailpit.json"
    data=json.loads(path.read_text())
    nodes={n["name"]:n for n in data["nodes"]}
    assert len(nodes)==7
    assert nodes["Customer Webhook"]["parameters"]["path"]=="rag-laya-intake"
    assert nodes["Customer Webhook"]["parameters"]["responseMode"]=="responseNode"
    assert nodes["Process AI"]["parameters"]["url"].endswith("/api/process")
    assert nodes["Send Review to Mailpit"]["parameters"]["url"].endswith("/api/notify")
    assert "Needs Review?" in data["connections"]
    assert all(n["parameters"]["respondWith"]=="json" for n in data["nodes"] if n["type"].endswith("respondToWebhook"))
