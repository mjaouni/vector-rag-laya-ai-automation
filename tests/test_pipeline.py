from service import pipeline
from service.decisions import classify
from service import decisions
from dataclasses import replace


def demo_decision(**overrides):
    x={"provider":"laya-local", "intent":"information", "confidence":0.9, "hazard_flag":False,"human_flag":False,"booking_flag":False,"needs_review":False}
    x.update(overrides)
    return x


def hit():
    return [{"source":"maintenance.md", "text":"Replace air filters", "score":0.9, "chunk":0, "id":"1"}]


def test_answer_path(monkeypatch):
    monkeypatch.setattr(pipeline, "classify", lambda _:demo_decision())
    monkeypatch.setattr(pipeline, "retrieve", lambda _:hit())
    monkeypatch.setattr(pipeline, "generate", lambda _q,_h:"Maintenance includes filters [maintenance.md]")
    x=pipeline.process_question("Tell me about routine maintenance", "a-1")
    assert x["status"]=="answered" and x["sources"]==["maintenance.md"]


def test_hazard_skips_retrieval(monkeypatch):
    monkeypatch.setattr(pipeline, "classify", lambda _:demo_decision(hazard_flag=True,needs_review=True))
    monkeypatch.setattr(pipeline, "retrieve", lambda _: (_ for _ in ()).throw(AssertionError("retrieval shouldn't run")))
    x=pipeline.process_question("Gas leak and smoke", "a-2")
    assert x["status"]=="needs_review" and x["reason"]=="potential_hazard"


def test_booking_does_not_generate(monkeypatch):
    monkeypatch.setattr(pipeline, "classify", lambda _:demo_decision(intent="booking",booking_flag=True,needs_review=True))
    monkeypatch.setattr(pipeline, "retrieve", lambda _:hit())
    monkeypatch.setattr(pipeline, "generate", lambda *_: (_ for _ in ()).throw(AssertionError("no booking generation")))
    x=pipeline.process_question("Book me tomorrow", "a-3")
    assert x["status"]=="needs_review" and "No booking" in x["answer"]


def test_no_evidence_fails_closed(monkeypatch):
    monkeypatch.setattr(pipeline, "classify", lambda _:demo_decision())
    monkeypatch.setattr(pipeline, "retrieve", lambda _:[])
    x=pipeline.process_question("Unanswerable", "a-4")
    assert x["status"]=="needs_review" and x["reason"]=="insufficient_evidence"


def test_laya_failure_is_not_faked(monkeypatch):
    monkeypatch.setattr(pipeline, "classify", lambda _: (_ for _ in ()).throw(ImportError("laya")))
    x=pipeline.process_question("hello there", "a-5")
    assert x["status"]=="needs_review" and x["decision"]["provider"]=="unavailable"


def test_rules_are_explicitly_labeled(monkeypatch):
    monkeypatch.setattr(decisions, "settings", replace(decisions.settings, decision_provider="rules"))
    x=classify("Please book an AC visit tomorrow")
    assert x["provider"]=="rules-only" and x["needs_review"]


def test_laya_prediction_contract(monkeypatch):
    class Fake:
        def predict(self, state, questions):
            assert state["body"]
            assert "intent" in questions
            return {"answers": {"intent":{"choice":"maintenance","confidence":0.94},"hazard":{"noul":0.03},"human":{"noul":0.01}},"routing":{"model":"english"}}
    monkeypatch.setattr(decisions, "settings", replace(decisions.settings, decision_provider="laya"))
    monkeypatch.setattr(decisions, "laya_router",lambda:Fake())
    x=classify("How should I maintain my AC?")
    assert x["provider"]=="laya-local" and not x["needs_review"]
