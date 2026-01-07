from fastapi import APIRouter, Query
from typing import List
from ..services.references import get_external_references

router = APIRouter()

@router.get("/search")
def search(q: str = Query(...), limit: int = 8):
    return {"results": get_external_references(q, limit=limit)}
