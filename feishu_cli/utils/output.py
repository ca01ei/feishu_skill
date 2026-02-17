"""Unified output formatting for Feishu CLI."""

import json
from typing import Any

import lark_oapi as lark


def format_response(response: Any) -> str:
    """Format an API response as JSON string."""
    if response.success():
        data = json.loads(lark.JSON.marshal(response.data)) if response.data else None
        return json.dumps({"success": True, "data": data}, ensure_ascii=False, indent=2)
    return format_error(
        code=response.code,
        msg=response.msg,
        log_id=response.get_log_id(),
    )


def format_error(code: int = 0, msg: str = "", log_id: str = "") -> str:
    """Format an error as JSON string."""
    result: dict[str, Any] = {"success": False, "code": code, "msg": msg}
    if log_id:
        result["log_id"] = log_id
    return json.dumps(result, ensure_ascii=False, indent=2)
