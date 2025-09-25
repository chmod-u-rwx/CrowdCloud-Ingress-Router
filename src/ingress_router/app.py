from uuid import UUID
from fastapi import FastAPI, WebSocket

from .routes import route_parser
from .routes import heartbeat
from .services.websocket_server_service import ingress_router_ws

app = FastAPI()
app.include_router(heartbeat.api_router)
app.include_router(route_parser.router)

@app.websocket("/ws/connect/{worker_id}")
async def master_node_websocket_connect(websocket: WebSocket, worker_id: UUID):
    await ingress_router_ws.connect(worker_id, websocket)
    print(f"Worker node: {worker_id}")

print(app.routes)