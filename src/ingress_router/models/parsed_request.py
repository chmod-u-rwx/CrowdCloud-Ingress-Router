from typing import Any, Dict
from pydantic import BaseModel

from ..models.payloads import MethodEnum

class ParsedRequest(BaseModel):
	path: str
	method: MethodEnum
	query_params: Dict[str, Any]
	headers: Dict[str, Any]
	body: Any
	subdomain: str
