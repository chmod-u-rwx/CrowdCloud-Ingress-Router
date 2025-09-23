import httpx
from fastapi import HTTPException
from ...config import CORE_API_URL
from ..models.requests import Requests

async def post_request_payload(client: httpx.AsyncClient, payload: Requests) -> dict:
    try:
        res = await client.post(
            f"{CORE_API_URL}/requests",
            json=payload.model_dump(mode="json"),
        )
        res.raise_for_status()
        return res.json()
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Error contacting CORE API (/requests): {e}",
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"CORE API /requests error: {e.response.text}",
        )