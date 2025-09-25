import httpx
from fastapi import HTTPException
from ...config import CORE_API_URL

async def get_resource_cost(client: httpx.AsyncClient) -> dict[str, float]:
	try:
		res = await client.get(f"{CORE_API_URL}/cost")
		res.raise_for_status()
	except httpx.RequestError as e:
		raise HTTPException(status_code=502, detail=f"Error contacting CORE API: {e}")
	except httpx.HTTPStatusError as e:
		raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
	return res.json()