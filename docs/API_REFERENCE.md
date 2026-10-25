# API reference

Default base URL: `http://localhost:8003`. Interactive schemas: `/docs`; OpenAPI: `/openapi.json`. Backend version: 1.0.1. JSON requests use `Content-Type: application/json`.

| Method / route | Authentication | Behavior |
|---|---|---|
| GET `/` | none | Serves the browser UI |
| GET `/healthz` | none | `ok`, service name, configured decision provider/model; no inference probe |
| GET `/api/status` | none | Collection existence/configuration; no model loading or Ollama connectivity test |
| GET `/docs`, `/redoc`, `/openapi.json` | none | Generated API documentation |
| POST `/api/process` | `X-Demo-Token` | Full policy/decision/retrieval/generation, no email |
| POST `/api/classify` | `X-Demo-Token` | Laya/rules decision object only |
| POST `/api/retrieve` | `X-Demo-Token` | `{"hits": [...]}`; no classification/generation |
| POST `/api/notify` | `X-Demo-Token` | Operator Mailpit SMTP notification and deduplication |
| POST `/api/via-n8n` | `X-Demo-Token` | Fixed configured n8n webhook proxy; full email workflow |

## Query input

```json
{
  "message": "What is included in routine AC maintenance?",
  "request_id": "demo-maintenance-001"
}
```

`message`: required string, 3–4000 characters. `request_id`: optional string, 1–128 characters, ASCII letters/digits/underscore/hyphen. If absent, processing generates a UUID. New logical requests should use new IDs; replaying an ID can suppress a notification.

Use the provided PowerShell script to read the local token without duplicating it in source:

```powershell
.\scripts\test_api.ps1 -Message 'What is included in routine AC maintenance?'
```

## Processing output

The [recorded maintenance response](evidence/maintenance.json) includes the actual run. Its shape is:

```json
{
  "request_id": "demo-maintenance-001",
  "status": "answered",
  "decision": {
    "provider": "laya-local",
    "intent": "maintenance",
    "confidence": 0.6997,
    "hazard_flag": false,
    "human_flag": false,
    "booking_flag": false,
    "needs_review": false
  },
  "answer": "Generated answer text with requested [maintenance.md] citations",
  "sources": ["maintenance.md"],
  "retrieved": [],
  "reason": "grounded_response"
}
```

This abbreviated example shows the schema, not a second claimed run; inspect the evidence for actual text/scores/passages. `retrieved` entries contain `id`, cosine `score`, `source`, `chunk`, and `text`. Laya decisions also include hazard/human probabilities and routing-model metadata; rules mode explicitly labels its provider `rules-only` and has no model confidence.

`needs_review` responses are normal HTTP 200 business outcomes. Reasons include `potential_hazard`, `human_or_booking_request`, `uncertain_classification`, `insufficient_evidence`, `retrieval_unavailable:<type>`, `generation_unavailable:<type>`, or decision-model failure. These responses do not imply that an employee has read or accepted the request.

## Notification input/output

Input fields: required `request_id`, `status`, and `answer`; optional `sources` (string array, default empty) and `reason` (default empty). The notification service accepts only `answered` and `needs_review`, and validates the request ID. This endpoint accepts the original process result; extra process fields are ignored by the input model.

Success: `{"notified":true,"deduplicated":false,"request_id":"..."}`. Replay: `{"notified":false,"deduplicated":true,"request_id":"..."}`. Recipient comes from server configuration, not request input.

## Errors

| Code | Condition |
|---|---|
| 401 | Missing/invalid token on a protected route |
| 422 | Invalid query/notification schema, message length, or query request-ID pattern |
| 503 | `/api/classify` model failure, `/api/retrieve` unavailable, or notification validation/SMTP failure |
| 502 | `/api/via-n8n` upstream failure, timeout, or non-JSON response |

Pipeline model/retrieval/generation failures generally return controlled review objects rather than HTTP 503. Status catches Qdrant failure and reports `indexed:false`. Error messages avoid including configured URLs with credentials or raw SMTP errors. The shared token is a development control, not per-user authorization.
