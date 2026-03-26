# backend/server/routes/health.py

from fastapi import APIRouter

router = APIRouter(tags=["health"])

@router.get("/health")
@router.get("/api/health")
def health():
    return {"ok": True}
