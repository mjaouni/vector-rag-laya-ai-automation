"""Safe setup and controlled failure paths, without model weights."""
from dataclasses import replace
from unittest.mock import Mock
import pytest
from fastapi.testclient import TestClient
import api
from service import decisions, pipeline, retrieval


def test_seed_preserves_existing_collection(monkeypatch):
    client = Mock()
    client.collection_exists.return_value = True
    monkeypatch.setattr(retrieval, 'qdrant', lambda: client)
    monkeypatch.setattr(retrieval, 'embedding_model', lambda: pytest.fail('Must not load embeddings'))
    assert retrieval.seed()['skipped'] is True
    client.delete_collection.assert_not_called()
    client.create_collection.assert_not_called()


def test_seed_and_retrieve_real_embedded_store(monkeypatch, tmp_path):
    from qdrant_client import QdrantClient
    class Array:
        def __init__(self, value): self.value = value
        def tolist(self): return self.value
    class Encoder:
        def encode(self, text, **kwargs):
            return Array([[1.0, 0.0] for _ in text] if isinstance(text, list) else [1.0, 0.0])
    docs = tmp_path / 'docs'
    docs.mkdir()
    (docs / 'maintenance.md').write_text('Replace the air filter.', encoding='utf-8')
    client = QdrantClient(path=str(tmp_path / 'qdrant'))
    monkeypatch.setattr(retrieval, 'settings', replace(retrieval.settings, docs_dir=docs, collection='test_only'))
    monkeypatch.setattr(retrieval, 'qdrant', lambda: client)
    monkeypatch.setattr(retrieval, 'embedding_model', lambda: Encoder())
    try:
        assert retrieval.seed()['documents'] == 1
        hits = retrieval.retrieve('routine maintenance')
        assert hits[0]['source'] == 'maintenance.md' and hits[0]['score'] == 1.0
        assert retrieval.seed()['skipped'] is True
    finally:
        client.close()


@pytest.mark.parametrize('confidence', [None, float('nan'), -0.1, 1.1, True])
def test_laya_invalid_confidence_requires_review(monkeypatch, confidence):
    router = Mock()
    router.predict.return_value = {'answers': {
        'intent': {'choice': 'maintenance', 'confidence': confidence},
        'hazard': {'noul': 0.01}, 'human': {'noul': 0.01}}}
    monkeypatch.setattr(decisions, 'settings', replace(decisions.settings, decision_provider='laya'))
    monkeypatch.setattr(decisions, 'laya_router', lambda: router)
    assert decisions.classify('Routine maintenance')['needs_review'] is True


def test_generation_failure_routes_to_review(monkeypatch):
    decision = dict(provider='laya-local', hazard_flag=False, booking_flag=False, human_flag=False, needs_review=False)
    monkeypatch.setattr(pipeline, 'classify', lambda _: decision)
    monkeypatch.setattr(pipeline, 'retrieve', lambda _: [{'source': 'maintenance.md'}])
    def fail(*args): raise TimeoutError('demo outage')
    monkeypatch.setattr(pipeline, 'generate', fail)
    result = pipeline.process_question('Routine maintenance')
    assert result['status'] == 'needs_review'
    assert result['reason'] == 'generation_unavailable:TimeoutError'


def test_request_id_is_validated_before_workflow():
    with TestClient(api.app) as client:
        response = client.post('/api/process', headers={'X-Demo-Token': api.settings.workflow_token},
                               json={'message': 'Routine maintenance', 'request_id': 'bad/id'})
    assert response.status_code == 422
