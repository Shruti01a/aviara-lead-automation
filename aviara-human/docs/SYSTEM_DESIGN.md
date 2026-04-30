# System Design Notes

## Architecture

```
                        ┌─────────────────────────────┐
  CRM / Web Form        │         n8n Workflow         │
  ─────POST────────────►│                              │
                        │  Webhook → Validate          │
                        │     → [Enrich | Classify]    │
                        │     → Merge → Filter         │
                        │     → Airtable + Slack       │
                        └─────────┬───────────┬────────┘
                                  │           │
                         POST /enrich    POST /classify
                                  │           │
                        ┌─────────▼───────────▼────────┐
                        │       FastAPI Service         │
                        │                               │
                        │  ┌──────────────────────┐    │
                        │  │   Redis Cache (L1)   │    │
                        │  └──────────┬───────────┘    │
                        │             │ miss            │
                        │  ┌──────────▼───────────┐    │
                        │  │  Enrichment / Claude │    │
                        │  └──────────────────────┘    │
                        └──────────────────────────────┘
                                       │
                        ┌──────────────▼───────────────┐
                        │        Celery Workers         │
                        │  process_lead → store + notify│
                        └──────────────────────────────┘
```

---

## Scalability — 1000+ leads/hour

1000 leads/hour is about 0.28/second — a single FastAPI pod handles this easily. But here's how to scale further:

**Horizontal scaling**: FastAPI pods are stateless, so you can add as many as needed behind a load balancer. Celery workers scale independently by adding more instances.

**Queue as buffer**: The webhook pushes to Celery immediately and returns 200. Workers process at their own pace. During a spike, leads queue up in Redis rather than timing out.

**Caching**: Redis caches both enrichment and classification results. If the same company keeps showing up (common in bulk imports), we skip the LLM call entirely.

**LLM rate limits**: For very high volume, use Anthropic's batch API. For now, the rule-based fallback kicks in if the API is slow.

---

## Reliability

**Retries**: n8n HTTP nodes retry 3x with 2s backoff. Celery tasks retry 3-5x with delays. This handles transient network issues cleanly.

**LLM fallback**: If Anthropic API fails, we automatically fall back to the keyword-based classifier. The response still comes back — just without the AI reasoning.

**Error visibility**: All errors go to a Slack alert + are logged. Nothing fails silently.

**Idempotency**: Not fully implemented in this version — would add a Redis SET NX check on `email + time bucket` to prevent duplicate processing from retried webhooks.

---

## Rate Limiting

Currently: API key required on all endpoints (401 on missing/wrong key).

For production I'd add `slowapi` with Redis-backed per-key rate limiting:

```python
from slowapi import Limiter
limiter = Limiter(key_func=lambda req: req.headers.get("x-api-key"))

@app.post("/classify")
@limiter.limit("30/minute")
async def classify(...):
    ...
```

Also nginx in front for IP-level rate limiting before requests even hit FastAPI.

---

## What I'd add with more time

- Real enrichment API (Clearbit or Hunter.io) instead of mock
- PostgreSQL for lead history + dedup at DB level
- Idempotency key check in Redis (5-10 min window)
- OpenTelemetry for distributed tracing across n8n → API → LLM
- Kubernetes + HPA scaling on queue depth
- Proper DLQ — tasks that fail completely go to a dead-letter queue for manual review
