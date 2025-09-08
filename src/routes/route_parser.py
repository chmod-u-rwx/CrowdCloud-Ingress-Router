import json
from uuid import UUID, uuid4
from fastapi import Request, APIRouter
from typing import Any
from src.models.parsed_request import ParsedRequest
from src.services.websocket_server_service import ingress_router_ws
from src.models.payloads import JobRequestPayload, JobResponsePayload, MethodEnum

router = APIRouter()

@router.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def catch_all(full_path: str, request: Request) -> dict[str, Any]:
    print("patj\n\n\n")
    body = await request.body()
    parsed = ParsedRequest(
        path = full_path,
        method = MethodEnum(request.method),
        query_params = dict(request.query_params),
        headers = dict(request.headers),
        body = json.loads(body) if body else None,
        subdomain = str(request.base_url).split("//")[1].split(".")[0]
    )

    request_id = uuid4()
    # master_id, worker_id = get_master_worker_from_ai(parsed)
    master_id = UUID("550e8400-e29b-41d4-a716-446655440000")
    worker_id = UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6")

    job_response: JobResponsePayload = await ingress_router_ws.send_job_rpc_to_master_node(
        job_payload=JobRequestPayload(
            request_id=request_id,
            job_id=parsed.subdomain,
            master_id=master_id,
            worker_id=worker_id,
            method=parsed.method,
            path=parsed.path,
            headers=parsed.headers,
            params=parsed.query_params,
            body=parsed.body
        ), master_id=master_id
    )
    
    return job_response.model_dump(mode="json")



def get_master_worker_from_ai(parsed: ParsedRequest):
    # lagay ko na muna to dito 
    pass