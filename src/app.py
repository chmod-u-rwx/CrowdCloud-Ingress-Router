from uuid import UUID
from fastapi import FastAPI, WebSocket
from src.routes import route_parser
from src.services.websocket_server_service import ingress_router_ws

app = FastAPI()
app.include_router(route_parser.router)

@app.websocket("/ws/connect/{worker_id}")
async def master_node_websocket_connect(websocket: WebSocket, worker_id: UUID):
    await ingress_router_ws.connect(worker_id, websocket)
    print(f"Worker node: {worker_id}")