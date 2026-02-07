"""Validation routes."""

from __future__ import annotations

import httpx
from fastapi import APIRouter, HTTPException

from models import ValidateLlamaKeyRequest, ValidateLlamaKeyResponse

router = APIRouter(tags=["validation"])


@router.post("/validate-llama-key", response_model=ValidateLlamaKeyResponse)
async def validate_llama_key(request: ValidateLlamaKeyRequest) -> ValidateLlamaKeyResponse:
    """Validate LlamaCloud API key by probing projects endpoint."""
    api_key = request.api_key.strip()
    if not api_key.startswith("llx-"):
        raise HTTPException(
            status_code=400,
            detail="Invalid API key format. LlamaCloud keys start with 'llx-'.",
        )

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://api.cloud.llamaindex.ai/api/v1/projects",
                headers={"Authorization": f"Bearer {api_key}"},
            )
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=f"Failed to reach LlamaCloud: {exc}") from exc

    if response.status_code == 401:
        raise HTTPException(status_code=401, detail="Invalid LlamaCloud API key.")
    if response.status_code == 403:
        raise HTTPException(status_code=403, detail="API key lacks LlamaCloud permissions.")
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail="LlamaCloud validation failed.")

    return ValidateLlamaKeyResponse(valid=True, message="API key is valid")
