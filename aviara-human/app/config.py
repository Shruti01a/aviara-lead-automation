import os
from dotenv import load_dotenv

load_dotenv()

# app settings
APP_NAME = "Lead Automation API"
VERSION = "1.0.0"

# auth
API_KEY = os.getenv("API_KEY", "my-local-dev-key")

# anthropic
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
USE_MOCK = os.getenv("USE_MOCK", "true").lower() == "true"

# redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# celery
CELERY_BROKER = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
CELERY_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")

# integrations (optional)
SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK_URL", "")
AIRTABLE_KEY = os.getenv("AIRTABLE_API_KEY", "")
AIRTABLE_BASE = os.getenv("AIRTABLE_BASE_ID", "")
