from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Any

class RunEngineRequest(BaseModel):
    html: Optional[str] = None
    text: Optional[str] = None
    phase: Literal["prepublish","publish"] = "prepublish"
    imported_urls: List[str] = []
    published_topics: List[dict] = []
    draft_topics: List[dict] = []
    buckets: dict = {}  # {"strong":[...], "optional":[...], "external":[...]}

class Candidate(BaseModel):
    anchor: dict
    target: dict
    bucket: Literal["strong","optional","external"]
    finalScore: float
    suggestions: Optional[List[dict]] = None
    posCues: Optional[List[str]] = None
    posBoost: Optional[float] = 0.0

class RunEngineResponse(BaseModel):
    recommended: List[Candidate] = []
    optional: List[Candidate] = []
    external: List[Candidate] = []
    hidden: List[Any] = []
    meta: dict = Field(default_factory=dict)

class UploadResponse(BaseModel):
    # Identity / metadata
    doc_id: str
    filename: str
    ext: str

    # Optional lightweight preview payloads (used only for simple types)
    text: str = ""
    html: str = ""

    # Backend-owned contract for frontend rendering/downloading
    original_url: str
    preview_url: str
    preview_mime: str
    preview_kind: Literal["pdf", "html", "text", "image", "download"]
