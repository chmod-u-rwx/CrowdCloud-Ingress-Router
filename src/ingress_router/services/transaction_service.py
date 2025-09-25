import httpx
from fastapi import HTTPException
from ...config import CORE_API_URL
from ..models.transaction import Transaction

async def post_transaction_payload(client: httpx.AsyncClient, payload: Transaction) -> dict:
    try:
        res = await client.post(
            f"{CORE_API_URL}/transactions",
            json=payload.model_dump(mode="json"),
        )
        res.raise_for_status()
        return res.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Error contacting CORE API (/transactions): {e}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"CORE API /transactions error: {e.response.text}")
