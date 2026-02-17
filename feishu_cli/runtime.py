"""Runtime helpers shared across command modules."""

from typing import Any, Callable

import lark_oapi as lark

from feishu_cli.auth.session import resolve_user_request_option


def call_api(client: lark.Client, api_method: Callable[..., Any], request: Any) -> Any:
    """Call SDK API method with user-priority auth option when available."""
    option = resolve_user_request_option(client)
    if option is None:
        return api_method(request)
    return api_method(request, option)
