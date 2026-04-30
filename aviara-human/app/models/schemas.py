from pydantic import BaseModel, EmailStr
from typing import Optional


# --- enrich ---

class EnrichRequest(BaseModel):
    name: str
    email: EmailStr
    company: str

class EnrichResponse(BaseModel):
    linkedin_url: Optional[str] = None
    company_size: Optional[str] = None
    industry: Optional[str] = None
    headquarters: Optional[str] = None


# --- classify ---

class ClassifyRequest(BaseModel):
    message: str

class ClassifyResponse(BaseModel):
    intent: str
    confidence: float
    reasoning: Optional[str] = None


# --- health ---

class HealthResponse(BaseModel):
    status: str
    version: str
