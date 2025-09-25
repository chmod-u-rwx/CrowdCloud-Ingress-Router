import json
import httpx
from uuid import UUID, uuid4
from fastapi import Request, APIRouter
from typing import Any
# from ..ingress_router.models.type_dict import Job
from ..models.type_dict import Job
from ..models.parsed_request import ParsedRequest
from ..models.requests import Requests, RequestStatus
from ..models.transaction import Transaction
from ..services.websocket_server_service import ingress_router_ws
from ..models.payloads import JobRequestPayload, JobResponsePayload, MethodEnum
from ..router import router as ai_router
from ..services.cost_service import get_resource_cost
from ..services.requests_service import post_request_payload
from ..services.transaction_service import post_transaction_payload

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
    worker_master_dict = ai_router.select_worker(job=Job(job_id=UUID(parsed.subdomain)))
    master_id = worker_master_dict["master_id"]
    worker_id = worker_master_dict["worker_id"]
    
    # job_request_payload = JobRequestPayload(
    # request_id=request_id,
    # job_id=parsed.subdomain,
    # master_id=master_id,
    # worker_id=worker_id,
    # method=parsed.method,
    # path=parsed.path,
    # headers=parsed.headers,
    # params=parsed.query_params,
    # body=parsed.body
    # )
    
    # job_response_payload: JobResponsePayload = await ingress_router_ws.send_job_rpc_to_master_node(
    #     job_payload=job_request_payload, 
    #     master_id=master_id
    # )

    # transaction_id = uuid4()
    # execution_time = job_response_payload.meta["runtime"]

    # requests_payload: Requests = Requests(
    #     request_id = request_id,
    #     job_id = UUID(parsed.subdomain),
    #     worker_id = worker_id,
    #     vm_id = uuid4(),
    #     request_payload = job_request_payload,
    #     response_payload = job_response_payload,
    #     status = RequestStatus.SUCCESS if 200 <= job_response_payload.status_code < 300 else RequestStatus.FAILED,
    #     execution_time = execution_time,
    #     transaction_id = transaction_id
    # )

    # async with httpx.AsyncClient() as client:

    #     resource_cost = await get_resource_cost(client=client)
    #     cost_ram = resource_cost["ram_gb_cost_per_second"]
    #     cost_cpu = resource_cost["cpu_core_cost_per_second"]
    #     total_cost = (cost_ram * execution_time) + (cost_cpu * execution_time)

    #     transaction_payload: Transaction = Transaction(
    #         transaction_id = transaction_id,
    #         request_id = request_id,
    #         job_id = UUID(parsed.subdomain),
    #         worker_id = worker_id,
    #         cost_ram = cost_ram,
    #         cost_cpu = cost_cpu,
    #         execution_time = execution_time,
    #         total_cost = total_cost
    #     )

    #     await post_request_payload(client=client, payload=requests_payload)
    #     await post_transaction_payload(client=client, payload=transaction_payload)
    
    # return job_response_payload.model_dump(mode="json")
