# Real screenshot index

Captured with Playwright from running services on 26 October 2026 (Asia/Beirut). Images are original browser captures, not generated mockups or reconstructed interfaces. The application token field was cleared before capture. The n8n validation account and Mailpit recipients use fictional `.test` addresses. Published images were visually inspected for secrets and unrelated personal data.

The existing authenticated native-browser window could not be accessed through the app approval flow. An isolated fresh n8n/Mailpit stack was used instead, with real imported workflow execution and the consolidated API. See [provenance and alternate ports](../DEMO_WALKTHROUGH.md). This avoided exposing unrelated FieldFlow workflows or inbox contents.

| File | Caption |
|---|---|
| [application-home.png](application-home.png) | Actual FastAPI-served home page before submission. |
| [application-answer.png](application-answer.png) | Successful maintenance response and retrieved filename list; token field cleared. |
| [application-diagnostics.png](application-diagnostics.png) | Expanded diagnostic JSON showing Laya maintenance intent, scores, review flags, and retrieval data. |
| [application-sources.png](application-sources.png) | The same response with the JSON panel scrolled to retrieved Qdrant passages and scores. |
| [n8n-workflow.png](n8n-workflow.png) | Seven-node imported workflow with both answer and review branches. |
| [n8n-webhook.png](n8n-webhook.png) | Real Customer Webhook settings: POST path, local test URL, response-node mode; no secret header value. |
| [n8n-execution.png](n8n-execution.png) | Successful maintenance execution with the answer branch highlighted. |
| [n8n-notification.png](n8n-notification.png) | Actual answer notification node output confirming SMTP notification delivery. |
| [mailpit-inbox.png](mailpit-inbox.png) | Isolated inbox containing only synthetic project test notifications. |
| [mailpit-email.png](mailpit-email.png) | Opened maintenance email with matching request ID, status, generated answer, and source list. |
| [mailpit-review.png](mailpit-review.png) | Opened safety-review notification for the live gas-odor scenario. |

The answer images deliberately retain the observed `[source.md]` citation failure. See [the walkthrough](../DEMO_WALKTHROUGH.md); these screenshots are evidence of current behavior, not a claim that all output is correct.

To recapture manually, start the stack, submit a new fictional maintenance question, clear the token field, open diagnostics, and capture the UI. In n8n, use the matching execution ID, fit the canvas, and open the notification node output without opening credential values. In Mailpit, filter to that request ID and capture inbox plus opened message. Verify every image before adding it to Git. Never capture account settings, raw credentials, private emails, or unrelated workflows.
