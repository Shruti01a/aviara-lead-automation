"""
Celery background worker for async lead processing.

Run with:
    celery -A workers.tasks worker --loglevel=info
"""

import httpx
from celery import Celery
from celery.utils.log import get_task_logger
from app import config

logger = get_task_logger(__name__)

celery_app = Celery(
    "lead_workers",
    broker=config.CELERY_BROKER,
    backend=config.CELERY_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    # ack only after task finishes - safer for retries
    task_acks_late=True,
)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def process_lead(self, lead_data: dict):
    """
    Full async pipeline: enrich → classify → store → notify
    Triggered after webhook receives a lead.
    """
    email = lead_data.get("email")
    logger.info(f"Processing lead async: {email}")

    try:
        headers = {"x-api-key": config.API_KEY}
        base = "http://localhost:8000"

        with httpx.Client(timeout=15) as client:
            # enrich
            enrich_resp = client.post(f"{base}/enrich", json=lead_data, headers=headers)
            enrich_resp.raise_for_status()
            enriched = enrich_resp.json()

            # classify - use company name as fallback message
            message = lead_data.get("message", f"Enquiry from {lead_data.get('company', '')}")
            classify_resp = client.post(
                f"{base}/classify",
                json={"message": message},
                headers=headers
            )
            classify_resp.raise_for_status()
            classified = classify_resp.json()

        full_data = {**lead_data, **enriched, **classified}

        # fire storage + notification as sub-tasks
        store_lead.delay(full_data)
        notify_team.delay(full_data)

        return {"status": "done", "email": email}

    except Exception as exc:
        logger.error(f"Lead processing failed for {email}: {exc}")
        # retry with backoff, then give up
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=5, default_retry_delay=10)
def store_lead(self, data: dict):
    """Save lead to Airtable."""
    if not config.AIRTABLE_KEY:
        logger.info("Airtable not configured, skipping storage")
        return

    try:
        url = f"https://api.airtable.com/v0/{config.AIRTABLE_BASE}/Leads"
        headers = {
            "Authorization": f"Bearer {config.AIRTABLE_KEY}",
            "Content-Type": "application/json"
        }
        record = {
            "fields": {
                "Name": data.get("name"),
                "Email": data.get("email"),
                "Company": data.get("company"),
                "Industry": data.get("industry"),
                "Company Size": data.get("company_size"),
                "Intent": data.get("intent"),
                "Confidence": data.get("confidence"),
            }
        }
        with httpx.Client(timeout=10) as client:
            resp = client.post(url, json=record, headers=headers)
            resp.raise_for_status()

        logger.info(f"Stored lead in Airtable: {data.get('email')}")

    except Exception as exc:
        logger.error(f"Airtable storage failed: {exc}")
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=15)
def notify_team(self, data: dict):
    """Send Slack notification for new lead."""
    if not config.SLACK_WEBHOOK:
        logger.info("Slack not configured, skipping notification")
        return

    try:
        msg = {
            "text": (
                f"*New Lead: {data.get('name')}*\n"
                f"Email: {data.get('email')}\n"
                f"Company: {data.get('company')} | {data.get('industry', 'Unknown')}\n"
                f"Size: {data.get('company_size', 'Unknown')}\n"
                f"Intent: `{data.get('intent')}` ({data.get('confidence', 0):.0%} confidence)"
            )
        }
        with httpx.Client(timeout=8) as client:
            resp = client.post(config.SLACK_WEBHOOK, json=msg)
            resp.raise_for_status()

        logger.info(f"Slack notified for lead: {data.get('email')}")

    except Exception as exc:
        logger.error(f"Slack notification failed: {exc}")
        raise self.retry(exc=exc)
