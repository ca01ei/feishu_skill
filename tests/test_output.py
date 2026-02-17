import json
from unittest.mock import MagicMock
from feishu_cli.utils.output import format_response, format_error


def test_format_response_success():
    mock_resp = MagicMock()
    mock_resp.success.return_value = True
    mock_resp.data = None
    result = format_response(mock_resp)
    parsed = json.loads(result)
    assert parsed["success"] is True
    assert parsed["data"] is None


def test_format_response_failure():
    mock_resp = MagicMock()
    mock_resp.success.return_value = False
    mock_resp.code = 99991400
    mock_resp.msg = "token invalid"
    mock_resp.get_log_id.return_value = "log123"
    result = format_response(mock_resp)
    parsed = json.loads(result)
    assert parsed["success"] is False
    assert parsed["code"] == 99991400
    assert parsed["msg"] == "token invalid"


def test_format_error():
    result = format_error(code=99991400, msg="token invalid")
    parsed = json.loads(result)
    assert parsed["success"] is False
    assert parsed["code"] == 99991400
    assert parsed["msg"] == "token invalid"


def test_format_error_with_log_id():
    result = format_error(code=1, msg="err", log_id="abc")
    parsed = json.loads(result)
    assert parsed["log_id"] == "abc"
