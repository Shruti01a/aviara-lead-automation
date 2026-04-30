# Aviara Lead Automation System

AI-powered lead enrichment + intent classification pipeline built with FastAPI, n8n, Redis, and Celery.

---

## What it does

Takes an incoming lead (name, email, company), enriches it with company data, classifies the lead's intent using AI, stores it in Airtable, and sends a Slack notification — all automated.

```
Webhook → Validate → Enrich + Classify → Filter → Airtable + Slack
```

---

## Tech Stack

- **FastAPI** — REST API (Python 3.11)
- **n8n** — workflow automation
- **Anthropic Claude** — intent classification (falls back to rule-based if not configured)
- **Redis** — caching + Celery broker
- **Celery** — async background processing
- **Docker Compose** — runs everything together

---

## Quick Start

```bash
# 1. clone the repo
git clone https://github.com/your-username/aviara-lead-automation
cd aviara-lead-automation

# 2. set up env file
cp .env.example .env
# you can leave everything as-is for local testing

# 3. start everything
docker compose up --build

# 4. test it's working
curl http://localhost:8000/health
```

**URLs:**
- API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs
- n8n: http://localhost:5678 (admin / changeme)

---

## API Reference

All endpoints require the `x-api-key` header.

### POST /enrich

Enriches a lead with company info.

```bash
curl -X POST http://localhost:8000/enrich \
  -H "x-api-key: my-local-dev-key" \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@techcorp.com", "company": "TechCorp"}'
```

Response:
```json
{
  "linkedin_url": "https://linkedin.com/in/john-doe",
  "company_size": "51-200 employees",
  "industry": "Technology",
  "headquarters": "United States"
}
```

### POST /classify

Classifies the intent of a message.

```bash
curl -X POST http://localhost:8000/classify \
  -H "x-api-key: my-local-dev-key" \
  -H "Content-Type: application/json" \
  -d '{"message": "I am interested in your services"}'
```

Response:
```json
{
  "intent": "sales_enquiry",
  "confidence": 0.92,
  "reasoning": "General interest in the product/services"
}
```

Possible intent values: `sales_enquiry`, `demo_request`, `pricing_enquiry`, `support_request`, `partnership`, `spam`

### GET /health

```bash
curl http://localhost:8000/health
```

---

## n8n Workflow Setup

1. Open n8n at http://localhost:5678
2. New workflow → Import from file → select `n8n/workflow.json`
3. Set these environment variables in n8n settings:
   - `FASTAPI_BASE_URL` = `http://api:8000`
   - `FASTAPI_API_KEY` = value from your `.env`
   - `SLACK_WEBHOOK_URL`, `AIRTABLE_BASE_ID`, `AIRTABLE_API_KEY` (optional)
4. Activate the workflow

To test the webhook manually:
```bash
curl -X POST http://localhost:5678/webhook/lead-intake \
  -H "Content-Type: application/json" \
  -d '{"name": "Jane Smith", "email": "jane@acme.com", "company": "Acme Inc"}'
```

---

## Running Without Docker

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env

# start API
uvicorn app.main:app --reload

# start celery worker (separate terminal)
celery -A workers.tasks worker --loglevel=info
```

---

## Running Tests

```bash
pytest tests/ -v
```

---

## Project Structure

```
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # env vars / settings
│   ├── models/
│   │   └── schemas.py       # Pydantic models
│   ├── routers/
│   │   ├── enrich.py        # POST /enrich
│   │   ├── classify.py      # POST /classify
│   │   └── health.py        # GET /health
│   ├── services/
│   │   ├── enrichment_service.py     # enrichment logic
│   │   └── classification_service.py # AI intent classification
│   └── utils/
│       ├── auth.py          # API key validation
│       ├── cache.py         # Redis caching
│       └── logger.py        # logging setup
├── workers/
│   └── tasks.py             # Celery async tasks
├── n8n/
│   └── workflow.json        # n8n workflow export
├── tests/
│   └── test_api.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

---

## Design Decisions

**Why rule-based fallback?**
The classifier works even without an LLM API key — useful for local dev, CI, and as a safety net if Anthropic has downtime. When `ANTHROPIC_API_KEY` is set, it uses Claude automatically.

**Why Redis caching?**
Same lead coming in multiple times (common with CRM integrations) shouldn't hit the LLM API every time. Cache is keyed on a hash of the input so results are consistent.

**Why Celery?**
The webhook needs to respond fast. Heavy work (storing to Airtable, sending Slack) runs in the background without blocking the HTTP response.

**Scalability (brief)**
For 1000+ leads/hour: scale API pods horizontally (stateless), increase Celery concurrency, use Redis Cluster for cache. The queue acts as a buffer during traffic spikes — workers process at their own pace.
