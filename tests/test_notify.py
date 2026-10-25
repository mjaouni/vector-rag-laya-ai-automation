from service import notify

def test_mailpit_notification_and_dedup(monkeypatch, tmp_path):
    monkeypatch.setattr(notify,"DB",tmp_path / "notify.sqlite3")
    sent=[]
    class SMTP:
        def __init__(self,*args,**kwargs): pass
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def send_message(self,m):sent.append(m)
    monkeypatch.setattr(notify.smtplib,"SMTP",SMTP)
    data={"request_id":"test-r-1", "status":"needs_review", "answer":"Please review", "sources":["safety.md"]}
    first=notify.send_notification(data)
    second=notify.send_notification(data)
    assert first['notified'] is True and second['deduplicated'] is True
    assert len(sent)==1 and 'review' in sent[0]['Subject']
