"""Tests for wiki commands."""

import json
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from feishu_cli.commands.wiki import wiki_app

runner = CliRunner()


# --- Space commands ---


@patch("feishu_cli.commands.wiki.create_client")
def test_wiki_space_list(mock_create_client: MagicMock) -> None:
    """Test listing wiki spaces."""
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.success.return_value = True
    mock_resp.data = None
    mock_client.wiki.v2.space.list.return_value = mock_resp
    mock_create_client.return_value = mock_client

    result = runner.invoke(wiki_app, ["space", "list"])

    assert result.exit_code == 0
    parsed = json.loads(result.stdout)
    assert parsed["success"] is True

@patch("feishu_cli.commands.wiki.create_client")
def test_wiki_space_create_invalid_json(mock_create_client: MagicMock) -> None:
    mock_create_client.return_value = MagicMock()
    result = runner.invoke(wiki_app, ["space", "create", "--data", "{"])
    assert result.exit_code == 2
    parsed = json.loads(result.stdout)
    assert parsed["success"] is False
    assert parsed["code"] == 2
    assert "Invalid JSON" in parsed["msg"]


@patch("feishu_cli.commands.wiki.create_client")
def test_wiki_space_list_failure(mock_create_client: MagicMock) -> None:
    """Test listing wiki spaces when API fails."""
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.success.return_value = False
    mock_resp.code = 99999
    mock_resp.msg = "permission denied"
    mock_resp.get_log_id.return_value = "log123"
    mock_client.wiki.v2.space.list.return_value = mock_resp
    mock_create_client.return_value = mock_client

    result = runner.invoke(wiki_app, ["space", "list"])

    assert result.exit_code == 1
    parsed = json.loads(result.stdout)
    assert parsed["success"] is False
    assert parsed["code"] == 99999


@patch("feishu_cli.commands.wiki.create_client")
def test_wiki_space_create(mock_create_client: MagicMock) -> None:
    """Test creating a wiki space."""
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.success.return_value = True
    mock_resp.data = None
    mock_client.wiki.v2.space.create.return_value = mock_resp
    mock_create_client.return_value = mock_client

    result = runner.invoke(wiki_app, ["space", "create", "--data", '{"name":"Test Space"}'])

    assert result.exit_code == 0
    parsed = json.loads(result.stdout)
    assert parsed["success"] is True


@patch("feishu_cli.commands.wiki.create_client")
def test_wiki_space_get(mock_create_client: MagicMock) -> None:
    """Test getting a wiki space."""
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.success.return_value = True
    mock_resp.data = None
    mock_client.wiki.v2.space.get.return_value = mock_resp
    mock_create_client.return_value = mock_client

    result = runner.invoke(wiki_app, ["space", "get", "--space", "spaceXXX"])

    assert result.exit_code == 0
    parsed = json.loads(result.stdout)
    assert parsed["success"] is True


@patch("feishu_cli.commands.wiki.create_client")
def test_wiki_space_get_node(mock_create_client: MagicMock) -> None:
    """Test getting node info for a wiki space."""
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.success.return_value = True
    mock_resp.data = None
    mock_client.wiki.v2.space.get_node.return_value = mock_resp
    mock_create_client.return_value = mock_client

    result = runner.invoke(wiki_app, ["space", "get-node", "--token", "tokenXXX"])

    assert result.exit_code == 0
    parsed = json.loads(result.stdout)
    assert parsed["success"] is True


# --- Node commands ---


@patch("feishu_cli.commands.wiki.create_client")
def test_wiki_node_create(mock_create_client: MagicMock) -> None:
    """Test creating a wiki node."""
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.success.return_value = True
    mock_resp.data = None
    mock_client.wiki.v2.space_node.create.return_value = mock_resp
    mock_create_client.return_value = mock_client

    result = runner.invoke(
        wiki_app, ["node", "create", "--space", "spaceXXX", "--data", '{"title":"Test"}']
    )

    assert result.exit_code == 0
    parsed = json.loads(result.stdout)
    assert parsed["success"] is True


@patch("feishu_cli.commands.wiki.create_client")
def test_wiki_node_list(mock_create_client: MagicMock) -> None:
    """Test listing wiki nodes."""
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.success.return_value = True
    mock_resp.data = None
    mock_client.wiki.v2.space_node.list.return_value = mock_resp
    mock_create_client.return_value = mock_client

    result = runner.invoke(wiki_app, ["node", "list", "--space", "spaceXXX"])

    assert result.exit_code == 0
    parsed = json.loads(result.stdout)
    assert parsed["success"] is True


@patch("feishu_cli.commands.wiki.create_client")
def test_wiki_node_copy(mock_create_client: MagicMock) -> None:
    """Test copying a wiki node."""
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.success.return_value = True
    mock_resp.data = None
    mock_client.wiki.v2.space_node.copy.return_value = mock_resp
    mock_create_client.return_value = mock_client

    result = runner.invoke(
        wiki_app,
        ["node", "copy", "--space", "spaceXXX", "--node", "nodeXXX", "--data", '{"target":"t"}'],
    )

    assert result.exit_code == 0


@patch("feishu_cli.commands.wiki.create_client")
def test_wiki_node_move(mock_create_client: MagicMock) -> None:
    """Test moving a wiki node."""
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.success.return_value = True
    mock_resp.data = None
    mock_client.wiki.v2.space_node.move.return_value = mock_resp
    mock_create_client.return_value = mock_client

    result = runner.invoke(
        wiki_app,
        ["node", "move", "--space", "spaceXXX", "--node", "nodeXXX", "--data", '{"target":"t"}'],
    )

    assert result.exit_code == 0


# --- Member commands ---


@patch("feishu_cli.commands.wiki.create_client")
def test_wiki_member_create(mock_create_client: MagicMock) -> None:
    """Test adding a wiki member."""
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.success.return_value = True
    mock_resp.data = None
    mock_client.wiki.v2.space_member.create.return_value = mock_resp
    mock_create_client.return_value = mock_client

    result = runner.invoke(
        wiki_app, ["member", "create", "--space", "spaceXXX", "--data", '{"member_type":"user"}']
    )

    assert result.exit_code == 0


@patch("feishu_cli.commands.wiki.create_client")
def test_wiki_member_list(mock_create_client: MagicMock) -> None:
    """Test listing wiki members."""
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.success.return_value = True
    mock_resp.data = None
    mock_client.wiki.v2.space_member.list.return_value = mock_resp
    mock_create_client.return_value = mock_client

    result = runner.invoke(wiki_app, ["member", "list", "--space", "spaceXXX"])

    assert result.exit_code == 0


@patch("feishu_cli.commands.wiki.create_client")
def test_wiki_member_delete(mock_create_client: MagicMock) -> None:
    """Test deleting a wiki member."""
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.success.return_value = True
    mock_resp.data = None
    mock_client.wiki.v2.space_member.delete.return_value = mock_resp
    mock_create_client.return_value = mock_client

    result = runner.invoke(
        wiki_app,
        ["member", "delete", "--space", "spaceXXX", "--member-id", "m123", "--data", '{"member_type":"user"}'],
    )

    assert result.exit_code == 0


# --- Setting commands ---


@patch("feishu_cli.commands.wiki.create_client")
def test_wiki_setting_update(mock_create_client: MagicMock) -> None:
    """Test updating wiki space setting."""
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.success.return_value = True
    mock_resp.data = None
    mock_client.wiki.v2.space_setting.update.return_value = mock_resp
    mock_create_client.return_value = mock_client

    result = runner.invoke(
        wiki_app,
        ["setting", "update", "--space", "spaceXXX", "--data", '{"create_setting":"val"}'],
    )

    assert result.exit_code == 0


# --- Search command (v1) ---


@patch("feishu_cli.commands.wiki.create_client")
def test_wiki_search(mock_create_client: MagicMock) -> None:
    """Test searching wiki nodes."""
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.success.return_value = True
    mock_resp.data = None
    mock_client.wiki.v1.node.search.return_value = mock_resp
    mock_create_client.return_value = mock_client

    result = runner.invoke(wiki_app, ["search", "--data", '{"query":"test"}'])

    assert result.exit_code == 0
    parsed = json.loads(result.stdout)
    assert parsed["success"] is True
