# RAG automation workflow

Import [rag-laya-mailpit.json](rag-laya-mailpit.json) into your local n8n. This is the single canonical workflow export; it contains no token or local credential IDs and is inactive on import.

Follow [the integration guide](../docs/N8N_INTEGRATION.md) to select Header Auth in all three HTTP nodes, save/publish, submit a question, inspect the chosen branch, and verify Mailpit. The workflow calls Python's SMTP notification endpoint; it does not use an n8n Send Email node.

There is no automatic workflow provisioning in this release. Existing installations can keep their working workflow. Do not activate a duplicate workflow using the same webhook path.
