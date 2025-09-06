import json
from fastapi import Request, APIRouter

router = APIRouter()

router.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def catch_all(full_path: str, request: Request):
    body = await request.body()

    print("path", )

    return {
        "path": full_path,
        "method": request.method,
        "query_params": dict(request.query_params),
        "headers": dict(request.headers),
        "body": json.loads(body) if body else None,
        "subdomain": str(request.base_url).split("//")[1].split(".")[0]
    }