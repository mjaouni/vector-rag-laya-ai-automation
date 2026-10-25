from fastapi.testclient import TestClient
import api

def test_health_and_docs():
    client=TestClient(api.app)
    assert client.get('/healthz').json()['ok']
    assert client.get('/docs').status_code==200


def test_auth_required():
    client=TestClient(api.app)
    assert client.post('/api/process',json={'message':'test question'}).status_code==401


def test_api_process(monkeypatch):
    monkeypatch.setattr(api, 'process_question', lambda message, request_id=None: {'status':'answered','answer':'ok','message':message})
    client=TestClient(api.app)
    x=client.post('/api/process',headers={'X-Demo-Token':api.settings.workflow_token},json={'message':'test question'})
    assert x.status_code==200 and x.json()['status']=='answered'
