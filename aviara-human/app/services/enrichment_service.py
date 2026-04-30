import re
from app.models import EnrichRequest, EnrichResponse
from app.utils.cache import get_cache, set_cache, make_key
from app.utils.logger import get_logger

logger = get_logger(__name__)

# rough industry mapping based on company name keywords
INDUSTRY_KEYWORDS = {
    "tech": "Technology",
    "soft": "Software / SaaS",
    "health": "Healthcare",
    "finance": "Financial Services",
    "bank": "Financial Services",
    "edu": "Education",
    "retail": "Retail / E-Commerce",
    "media": "Media",
    "consult": "Consulting",
    "ai": "Artificial Intelligence",
    "data": "Data & Analytics",
}

# company size buckets - just use a hash of company name to pick one
# in real life you'd call Clearbit or Hunter.io here
SIZE_BUCKETS = [
    "1-10 employees",
    "11-50 employees",
    "51-200 employees",
    "201-500 employees",
    "1000+ employees",
]


def guess_industry(company: str) -> str:
    name = company.lower()
    for keyword, industry in INDUSTRY_KEYWORDS.items():
        if keyword in name:
            return industry
    return "General Business"


def mock_linkedin(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]", "-", name.lower()).strip("-")
    return f"https://linkedin.com/in/{slug}"


def mock_company_size(company: str) -> str:
    # deterministic - same company always gets same bucket
    idx = sum(ord(c) for c in company) % len(SIZE_BUCKETS)
    return SIZE_BUCKETS[idx]


async def enrich_lead(req: EnrichRequest) -> EnrichResponse:
    cache_key = make_key("enrich", {"email": req.email, "company": req.company})

    cached = get_cache(cache_key)
    if cached:
        logger.info(f"Cache hit for enrich: {req.email}")
        return EnrichResponse(**cached)

    # TODO: replace with real Clearbit/Hunter API call
    result = EnrichResponse(
        linkedin_url=mock_linkedin(req.name),
        company_size=mock_company_size(req.company),
        industry=guess_industry(req.company),
        headquarters="United States",  # would come from API in prod
    )

    set_cache(cache_key, result.model_dump())
    logger.info(f"Enriched lead: {req.email} | industry: {result.industry}")
    return result
