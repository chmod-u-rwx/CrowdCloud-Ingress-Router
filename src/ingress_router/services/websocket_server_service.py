import asyncio
import json
from typing import Any, Awaitable, Callable, Dict
from uuid import UUID
from asyncio import Future
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from ..models.payloads import (
    JobRequestPayload,
    JobResponsePayload,
    WebsocketMessage,
    MessageType
)

# ---- Exceptions ----

class MasterNotConnectedError(Exception):
    ...

class MasterCommunicationError(Exception):
    ...

class InvalidMasterResponseError(Exception):
    ...

class RPCRequestTimeoutError(asyncio.TimeoutError):
    ...

# ---- Master Node Server ----

class IngressRouterWebsocketServerService:
    def __init__(self):
        self.connections: Dict[str, WebSocket] = {}
        self.pending_requests: Dict[str, asyncio.Future[Any]] = {}
        self._handler: Dict[MessageType, Callable[[UUID, WebsocketMessage], Awaitable[None]]] = {
            MessageType.HEARTBEAT: self._handle_heartbeat,
            MessageType.STATUS_UPDATE: self._handle_status_update,
            MessageType.TASK_RESULT: self._handle_task_result,
            MessageType.JOB_RESPONSE: self._handle_job_response,
        }
    
    async def connect(self, master_id: UUID, websocket: WebSocket):
        await websocket.accept()
        master_key = str(master_id)
        self.connections[master_key] = websocket
    
        try:
            await self._handle_master_websocket_message(master_id, websocket)
        except WebSocketDisconnect:
            print(f"Master {master_id} disconnected normally")
        except Exception as e:
            print(f"Master {master_id} disconnected with an error: {e}")
        finally:
            if str(master_id) in self.connections:
                del self.connections[str(master_id)]
                print(f"Cleaned up connection for master {master_id}")

    # ---- Send to Master ----
    
    async def send_to_websocket_message_to_master(self, master_id: UUID, ws_message: WebsocketMessage):
        """
        Send arbitrary data to master (fire-and-forget style)
        """
        
        master_key = str(master_id)
        ws = self.connections.get(master_key)
        
        if not ws:
            print(f"Master {master_id} not connected")
            raise RuntimeError(f"Master {master_id} not connected")
        
        try:
            await self.send_websocket_message_to_master(master_id, ws_message)
        except Exception as e:
            print(f"Failed to send to master {master_id}: {e}")
            if master_key in self.connections:
                raise RuntimeError(f"Failed to send to master {master_id}: {e}")
    
    async def send_websocket_message_to_master(
        self,
        master_id: UUID,
        ws_message: WebsocketMessage
    ):
        ws = self._get_websocket_or_raise(master_id)
        
        try:
            message_data = ws_message.model_dump()
            await ws.send_json(message_data)
        except Exception as e:
            self.connections.pop(str(master_id), None)
            raise MasterCommunicationError(f"Failed to send to master {master_id}: {e}")

    async def send_job_rpc_to_master_node(
        self,
        master_id: UUID,
        job_payload: JobRequestPayload,
        timeout: float = 30.0
    ) -> JobResponsePayload:
        
        if not self.is_master_connected(master_id):
            raise MasterNotConnectedError(f"Master {master_id} not connected")
        
        ws = self._get_websocket_or_raise(master_id)
        
        request_id = job_payload.request_id
        
        response_future: Future[Any] = asyncio.Future()
        self.pending_requests[str(request_id)] = response_future
        
        ws_message = WebsocketMessage(
            type=MessageType.JOB_REQUEST,
            request_id=job_payload.request_id,
            payloads=job_payload.model_dump(),
        )
        
        try:
            await ws.send_json(ws_message.model_dump(mode="json"))
            print("sent job")
            response = await asyncio.wait_for(response_future, timeout=timeout)
            print("received")
            return response
        
        except ValidationError as ve:
            raise InvalidMasterResponseError(f"Invalid response from master: {ve}")
        except asyncio.TimeoutError as e:
            raise RPCRequestTimeoutError(f"Master {master_id} did not respond within {timeout} seconds") from e
        except Exception as e:
            raise RuntimeError(f"Failed to send job request to master {master_id}: {e}")
        
        finally:
            self.pending_requests.pop(str(request_id), None)
    
    async def _handle_master_websocket_message(
        self,
        master_id: UUID,
        websocket: WebSocket
    ):
        while True:
            try:
                raw_message = await websocket.receive_json()
                await self._process_message(master_id, websocket, raw_message)
            except json.JSONDecodeError:
                await self._send_error_response(websocket, "Invalid JSON format")
            except WebSocketDisconnect:
                break
            except Exception as e:
                print(f"Unexpected error processing message from {master_id}: {e}")
                await self._send_error_response(websocket, "Internal server error")
    
    async def _process_message(
        self,
        master_id: UUID,
        websocket: WebSocket,
        raw_message: Dict[str, Any]
    ) -> None:
        """Process a single message from master."""

        message = self._parse_message(raw_message)
        if message is None:
            await self._send_error_response(websocket, "Invalid message format")
            return
        
        handler = self._handler.get(message.type)
        if handler is None:
            await self._send_error_response(websocket, "Unknown message type")
            return
        
        try:
            await handler(master_id, message)
        except Exception as e:
            print(f"Handler error for {message.type} from {master_id}: {e}")
            await self._send_error_response(websocket, "Handler execution failed")
    
    def _parse_message(
        self,
        raw_message: Dict[str, Any]
    ) -> WebsocketMessage | None:
        """Parse raw message into WebsocketMessage. Returns None if invalid."""
        
        try:
            return WebsocketMessage(**raw_message)
        except ValidationError as e:
            print(f"Message validation failed: {e}")
            return None
    
    async def _send_error_response(self, websocket: WebSocket, error_message: str) -> None:
        """Send standardized error response to master."""
        
        error_response: Dict[str, Any] = {
            "type": MessageType.ERROR,
            "payloads": {"error": error_message}
        }
        try:
            await websocket.send_json(error_response)
        except Exception as e:
            print(f"Failed to send error response: {e}")

   
    # ---- Inbound Handler ----
    
    async def _handle_job_response(
        self,
        master_id: UUID,
        ws_message: WebsocketMessage
    ):
        request_id = str(ws_message.request_id) if ws_message.request_id else None
        if not request_id or request_id not in self.pending_requests:
            print(f"Dangling job response from {master_id} with request_id={ws_message.request_id}")
            return
        
        future = self.pending_requests[request_id]
        if future.done():
            return
        
        try:
            payload = JobResponsePayload(**ws_message.payloads)
            future.set_result(payload)
        except ValidationError as ve:
            future.set_exception(InvalidMasterResponseError(f"Invalid response payload: {ve}"))
            return
    
    async def _handle_heartbeat(self, master_id: UUID, msg: WebsocketMessage):
        print(f"Heartbeat from master {master_id}")
    
    async def _handle_status_update(self, master_id: UUID, msg: WebsocketMessage):
        print(f"Status update from master {master_id}: {msg.payloads}")

    async def _handle_task_result(self, master_id: UUID, msg: WebsocketMessage):
        print(f"Task result from master {master_id}: {msg.payloads}")
    
    # ----- Utilities -----
    
    def _get_websocket_or_raise(self, master_id: UUID) -> WebSocket:
        ws = self.connections.get(str(master_id))
        if not ws:
            raise MasterNotConnectedError(f"Master {master_id} not connected")
        return ws
    
    def get_connected_masters(self) -> list[str]:
        """Return list of connected master IDs"""
        
        return list(self.connections.keys())
    
    def is_master_connected(self, master_id: UUID) -> bool:
        """Check if master is connected"""
        
        return str(master_id) in self.connections
    
    def get_pending_requests_count(self) -> int:
        """Get count of pending RPC requests"""
        
        return len(self.pending_requests)
    
ingress_router_ws = IngressRouterWebsocketServerService()