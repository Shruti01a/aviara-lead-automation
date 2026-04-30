import json
import re
from app.models import ClassifyRequest, ClassifyResponse
from app.utils.cache import get_cache, set_cache, make_key
from app.utils import get_logger
from app import config

logger = get_logger(__name__)

# the system prompt - tells the LLM exactly what we want back
SYSTEM_PROMPT = """
You are a lead intent classifier for a B2B SaaS company.

Given a message from a potential lead, classify it into one of these intents:
- sales_enquiry: general interest in the product/services
- demo_request: wants a demo or trial
- pricing_enquiry: asking about pricing or plans
- support_request: needs help or has an issue
- partnership: wants to collaborate or partner
- spam: irrelevant or junk

Respond ONLY with a JSON object like this (no extra text, no markdown):
{
  "intent": "sales_enquiry",
  "confidence": 0.9,
  "reasoning": "one sentence explanation"
}
""".strip()


# simple keyword fallback if LLM is not configured
def rule_based_classify(message: str) -> ClassifyResponse:
    msg = message.lower()

    if not re.search(r"[a-z]", msg):
        return ClassifyResponse(intent="spam", confidence=0.95, reasoning="No readable text")

    if any(w in msg for w in ["demo", "trial", "walkthrough"]):
        return ClassifyResponse(intent="demo_request", confidence=0.88, reasoning="Demo-related keywords found")

    if any(w in msg for w in ["price", "pricing", "cost", "plan", "quote"]):
        return ClassifyResponse(intent="pricing_enquiry", confidence=0.87, reasoning="Pricing-related keywords found")

    if any(w in msg for w in ["partner", "collaborate", "integrate"]):
        return ClassifyResponse(intent="partnership", confidence=0.85, reasoning="Partnership-related keywords found")

    if any(w in msg for w in ["support", "issue", "bug", "help", "error"]):
        return ClassifyResponse(intent="support_request", confidence=0.85, reasoning="Support-related keywords found")

    if any(w in msg for w in ["interested", "service", "product", "learn", "info"]):
        return ClassifyResponse(intent="sales_enquiry", confidence=0.80, reasoning="Sales interest keywords found")

    return ClassifyResponse(intent="sales_enquiry", confidence=0.55, reasoning="Defaulted to sales enquiry")


async def classify_intent(req: ClassifyRequest) -> ClassifyResponse:
    cache_key = make_key("classify", {"message": req.message.lower()})

    cached = get_cache(cache_key)
    if cached:
        logger.info("Cache hit for classify")
        return ClassifyResponse(**cached)

    # use rule-based if mock mode or no API key set
    if config.USE_MOCK or not config.ANTHROPIC_API_KEY:
        result = rule_based_classify(req.message)
        result_dict = result.model_dump()
        set_cache(cache_key, result_dict)
        return result

    # real LLM call
    try:
        import anthropic
        client = anthropic.AsyncAnthropic(api_key=config.ANTHROPIC_API_KEY)

        response = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=200,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": req.message}]
        )

        raw = response.content[0].text.strip()

        # strip any accidental markdown fences
        raw = re.sub(r"```json|```", "", raw).strip()
        parsed = json.loads(raw)

        result = ClassifyResponse(
            intent=parsed["intent"],
            confidence=float(parsed["confidence"]),
            reasoning=parsed.get("reasoning")
        )

        set_cache(cache_key, result.model_dump())
        logger.info(f"LLM classified: {result.intent} ({result.confidence})")
        return result

    except Exception as e:
        logger.error(f"LLM failed, falling back to rules: {e}")
        result = rule_based_classify(req.message)
        set_cache(cache_key, result.model_dump())
        return result
