# 🚀 Aviara Lead Automation System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

**AI-powered lead enrichment and intent classification pipeline**

Built with FastAPI, n8n, Anthropic Claude, Redis, and Celery

[Features](#-features) • [Quick Start](#-quick-start) • [API Docs](#-api-reference) • [Architecture](#-architecture)

</div>

---

## 📋 Overview

Aviara Lead Automation is an intelligent lead processing system that automatically enriches incoming leads with company data, classifies their intent using AI, and routes them to the appropriate channels.

**What it does:**
- 📧 Receives leads via webhook (name, email, company)
- 🔍 Enriches with company data (size, industry, location)
- 🤖 Classifies intent using Anthropic Claude AI
- 📊 Stores qualified leads in Airtable
- 💬 Sends notifications to Slack
- ⚡ All automated and real-time

### Workflow

```
Webhook → Validate → Enrich + Classify → Filter → Airtable + Slack
```

---

## ✨ Features

### 🎯 **Intelligent Intent Classification**
- Powered by Anthropic Claude for accurate intent detection
- Fallback to rule-based classification for reliability
- Categories: Sales Enquiry, Demo Request, Pricing, Support, Partnership, Spam
- Confidence scoring for each classification

### 📈 **Lead Enrichment**
- Automatic company data lookup
- LinkedIn profile detection
- Company size and industry classification
- Headquarters location identification

### ⚡ **Performance & Scalability**
- Redis caching to reduce API calls
- Async background processing with Celery
- Horizontal scaling support
- Queue-based architecture for handling traffic spikes

### 🔒 **Security**
- API key authentication
- Environment variable management
- Input validation with Pydantic
- CORS protection

### 🐳 **Docker-First**
- Complete Docker Compose setup
- One-command deployment
- Isolated services
- Easy local development

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| **FastAPI** | REST API framework (Python 3.11) |
| **n8n** | Workflow automation & orchestration |
| **Anthropic Claude** | AI-powered intent classification |
| **Redis** | Caching & message broker |
| **Celery** | Async background task processing |
| **Docker** | Containerization & deployment |
| **Airtable** | CRM & lead storage |
| **Slack** | Real-time notifications |

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Git
- (Optional) Python 3.11+ for local development

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/shruti01a/aviara-lead-automation.git
cd aviara-lead-automation

# 2. Set up environment variables
cp .env.example .env
# Edit .env with your API keys (you can leave defaults for local testing)

# 3. Start all services
docker compose up --build

# 4. Verify it's running
curl http://localhost:8000/health
```

### Access Points

Once running, you can access:

| Service | URL | Credentials |
|---------|-----|-------------|
| **API** | http://localhost:8000 | API Key required |
| **API Docs** | http://localhost:8000/docs | - |
| **n8n** | http://localhost:5678 | admin / changeme |
| **Redis** | localhost:6379 | - |

---

## 📚 API Reference

All endpoints require the `x-api-key` header.

### Health Check

```bash
GET /health
```

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-04-30T10:30:00Z"
}
```

---

### Enrich Lead

```bash
POST /enrich
```

Enriches a lead with company information.

**Request:**
```bash
curl -X POST http://localhost:8000/enrich \
  -H "x-api-key: my-local-dev-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@techcorp.com",
    "company": "TechCorp"
  }'
```

**Response:**
```json
{
  "name": "John Doe",
  "email": "john@techcorp.com",
  "company": "TechCorp",
  "linkedin_url": "https://linkedin.com/in/john-doe",
  "company_size": "51-200 employees",
  "industry": "Technology",
  "headquarters": "United States"
}
```

---

### Classify Intent

```bash
POST /classify
```

Classifies the intent of a customer message.

**Request:**
```bash
curl -X POST http://localhost:8000/classify \
  -H "x-api-key: my-local-dev-key" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I would like to schedule a demo of your product"
  }'
```

**Response:**
```json
{
  "intent": "demo_request",
  "confidence": 0.95,
  "reasoning": "User explicitly requested a product demonstration"
}
```

**Intent Categories:**
- `sales_enquiry` - General interest in products/services
- `demo_request` - Request for product demonstration
- `pricing_enquiry` - Questions about pricing
- `support_request` - Technical support needed
- `partnership` - Partnership or collaboration interest
- `spam` - Spam or irrelevant message

---

## 🔄 n8n Workflow Setup

### Import Workflow

1. Open n8n at http://localhost:5678
2. Click **"New workflow"**
3. Click **"⋮"** → **"Import from file"**
4. Select `n8n/workflow.json`
5. Click **"Save"**

### Configure Environment Variables

Set these in your `.env` or n8n settings:

```bash
FASTAPI_BASE_URL=http://api:8000
FASTAPI_API_KEY=your-api-key
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
AIRTABLE_BASE_ID=appXXXXXXXXXXXXXX
AIRTABLE_API_KEY=keyXXXXXXXXXXXXXX
```

### Test the Webhook

```bash
curl -X POST http://localhost:5678/webhook/lead-intake \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Smith",
    "email": "jane@acme.com",
    "company": "Acme Inc",
    "message": "I need pricing information"
  }'
```

---

## 🏗️ Architecture

### System Components

```
┌─────────────────┐
│   n8n Webhook   │
│   (Port 5678)   │
└────────┬────────┘
         │
         v
┌─────────────────┐
│   FastAPI API   │
│   (Port 8000)   │
└────────┬────────┘
         │
         ├──────> Redis Cache (Port 6379)
         │        └── Caching enrichment results
         │
         ├──────> Anthropic Claude API
         │        └── Intent classification
         │
         v
┌─────────────────┐
│  Celery Worker  │
│ (Background)    │
└────────┬────────┘
         │
         ├──────> Airtable
         │        └── Store qualified leads
         │
         └──────> Slack
                  └── Send notifications
```

### Data Flow

1. **Webhook Trigger**: Lead data arrives via n8n webhook
2. **Validation**: FastAPI validates input data
3. **Enrichment**: Company data is fetched and enriched
4. **Classification**: Claude analyzes message intent
5. **Caching**: Results stored in Redis (24hr TTL)
6. **Background Processing**: Celery worker handles CRM/notifications
7. **Storage**: Qualified leads saved to Airtable
8. **Notification**: Team notified via Slack

---

## 📁 Project Structure

```
aviara-lead-automation/
├── app/
│   ├── main.py                      # FastAPI application entry point
│   ├── config.py                    # Configuration & environment variables
│   ├── models/
│   │   └── schemas.py               # Pydantic data models
│   ├── routers/
│   │   ├── enrich.py                # Lead enrichment endpoint
│   │   ├── classify.py              # Intent classification endpoint
│   │   └── health.py                # Health check endpoint
│   ├── services/
│   │   ├── enrichment_service.py    # Company data enrichment logic
│   │   └── classification_service.py # AI intent classification
│   └── utils/
│       ├── auth.py                  # API key authentication
│       ├── cache.py                 # Redis caching utilities
│       └── logger.py                # Logging configuration
├── workers/
│   └── tasks.py                     # Celery background tasks
├── n8n/
│   └── workflow.json                # n8n workflow configuration
├── tests/
│   └── test_api.py                  # API tests
├── docs/
│   └── SYSTEM_DESIGN.md             # Architecture documentation
├── Dockerfile                        # Docker configuration
├── docker-compose.yml                # Multi-service orchestration
├── requirements.txt                  # Python dependencies
├── .env.example                      # Environment variables template
└── README.md                         # This file
```

---

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# API Configuration
ENVIRONMENT=development
API_KEY=my-local-dev-key
HOST=0.0.0.0
PORT=8000

# AI Services
OPENAI_API_KEY=sk-...                    # Optional: For enrichment
ANTHROPIC_API_KEY=sk-ant-...             # Required: For intent classification

# Redis
REDIS_URL=redis://redis:6379/0

# n8n
N8N_ENCRYPTION_KEY=your-encryption-key
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=changeme

# Integrations (Optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
AIRTABLE_BASE_ID=appXXXXXXXXXXXXXX
AIRTABLE_API_KEY=keyXXXXXXXXXXXXXX
```

---

## 💻 Local Development

### Without Docker

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env

# Run Redis (required)
# Install Redis: https://redis.io/download
redis-server

# Run API server
uvicorn app.main:app --reload --port 8000

# Run Celery worker (separate terminal)
celery -A workers.tasks worker --loglevel=info
```

### Run Tests

```bash
# Install test dependencies
pip install pytest pytest-cov httpx

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

---

## 🎯 Use Cases

### Sales Team Automation
- Automatically qualify inbound leads
- Route high-intent leads to sales team
- Reduce manual lead qualification time by 80%

### Marketing Campaigns
- Track campaign performance by intent
- Identify product interest patterns
- Optimize messaging based on intent data

### Customer Support
- Automatically categorize support requests
- Route to appropriate team members
- Prioritize based on intent urgency

---

## 🔒 Security Best Practices

- ✅ All sensitive data in environment variables
- ✅ API key authentication required
- ✅ Input validation with Pydantic
- ✅ CORS protection enabled
- ✅ Rate limiting (recommended for production)
- ✅ No hardcoded credentials
- ✅ Docker security best practices

---

## 📈 Scaling Considerations

### For 100+ leads/hour:
- Current setup handles this easily
- Single API instance + Celery worker

### For 1,000+ leads/hour:
- Scale API horizontally (stateless)
- Add multiple Celery workers
- Use Redis Cluster for high availability

### For 10,000+ leads/hour:
- Load balancer (nginx/traefik)
- Redis Cluster with sharding
- Celery worker pools (10+ workers)
- Consider PostgreSQL for lead storage
- Monitoring with Prometheus/Grafana

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Add tests for new features
- Update documentation
- Keep commits atomic and meaningful

---

## 🐛 Troubleshooting

### API not responding
```bash
# Check if services are running
docker compose ps

# Check logs
docker compose logs api

# Restart services
docker compose restart
```

### Redis connection issues
```bash
# Test Redis connection
docker compose exec redis redis-cli ping
# Should return: PONG
```

### n8n workflow not triggering
```bash
# Check n8n logs
docker compose logs n8n

# Verify webhook URL is correct
# Test with curl (see n8n workflow section)
```

### Intent classification not working
```bash
# Verify Anthropic API key is set
echo $ANTHROPIC_API_KEY

# Check API logs for errors
docker compose logs api | grep -i "classification"
```

---

## 📝 Design Decisions

### Why Rule-Based Fallback?
The classifier works even without an LLM API key — useful for local dev, CI, and as a safety net if Anthropic has downtime. When `ANTHROPIC_API_KEY` is set, it uses Claude automatically.

### Why Redis Caching?
Same lead coming in multiple times (common with CRM integrations) shouldn't hit the LLM API every time. Cache is keyed on a hash of the input so results are consistent and cost-effective.

### Why Celery?
The webhook needs to respond fast (<100ms). Heavy work (storing to Airtable, sending Slack) runs in the background without blocking the HTTP response.

### Why Docker Compose?
Development-production parity. What runs on your laptop runs in production. No "works on my machine" issues.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Shruti Mishra**

- GitHub: [@shruti01a](https://github.com/shruti01a)
- LinkedIn: [Connect with me](https://linkedin.com/in/shruti843a)


---

## 🌟 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Amazing Python web framework
- [Anthropic Claude](https://www.anthropic.com/) - Powerful AI for intent classification
- [n8n](https://n8n.io/) - Workflow automation platform
- [Celery](https://docs.celeryproject.org/) - Distributed task queue

---

## ⭐ Show Your Support

Give a ⭐️ if this project helped you!

---

<div align="center">

**Built with ❤️ for automating lead workflows**

[Report Bug](https://github.com/shruti01a/aviara-lead-automation/issues) • [Request Feature](https://github.com/shruti01a/aviara-lead-automation/issues)

</div>
