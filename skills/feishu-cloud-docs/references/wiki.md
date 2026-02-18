# wiki 知识库操作参考

## 概述

`wiki` 命令操作飞书知识库（Wiki）。

**层级结构**：

```
Space（知识空间）  ← --space <space_id>
  └── Node（节点/页面）  ← --node <node_token>
```

**Token 获取方式**：
- `space_id`：通过 `wiki space list` 获取（不在 URL 中）
- `node_token`：从 URL `https://xxx.feishu.cn/wiki/<node_token>` 提取，或通过 `wiki node list` 获取

---

## 命令速览

| 命令 | 说明 |
|------|------|
| `wiki space list` | 列出所有知识空间 |
| `wiki space get` | 获取空间信息 |
| `wiki space create` | 新建知识空间 |
| `wiki space get-node` | 通过 node_token 查询所属空间 |
| `wiki node list` | **列出空间内的节点（页面）** |
| `wiki node create` | 新建节点（创建页面） |
| `wiki node copy` | 复制节点 |
| `wiki node move` | 移动节点 |
| `wiki member list/create/delete` | 成员管理 |
| `wiki setting update` | 空间设置 |
| `wiki search` | 搜索节点 |

---

## Space 操作

### wiki space list — 列出所有知识空间

```bash
scripts/feishu-cli.sh wiki space list
scripts/feishu-cli.sh wiki space list --page-size 20
```

响应示例：

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "space_id": "7012345678901234567",
        "name": "产品团队知识库",
        "description": "产品相关文档",
        "visibility": "private"
      }
    ]
  }
}
```

**`space_id` 就是所有其他 wiki 命令的 `--space` 参数值。**

### wiki space get — 获取空间信息

```bash
scripts/feishu-cli.sh wiki space get --space "7012345678901234567"
scripts/feishu-cli.sh wiki space get --space "7012345678901234567" --lang "zh"
```

### wiki space create — 新建知识空间

```bash
scripts/feishu-cli.sh wiki space create \
  --data '{"name":"新知识库","description":"描述","visibility":"private"}'
```

`visibility` 取值：`private`（私有）或 `public`（公开）

### wiki space get-node — 通过 node_token 查询所属空间

```bash
# 当只有 node_token 不知道 space_id 时使用
scripts/feishu-cli.sh wiki space get-node --token "wikcnXXXX1234"
```

---

## Node 操作

### wiki node list — 列出节点

```bash
# 列出空间根节点
scripts/feishu-cli.sh wiki node list --space "7012345678901234567"

# 列出某个节点的子节点
scripts/feishu-cli.sh wiki node list \
  --space "7012345678901234567" \
  --parent "wikcnXXXX1234"

# 分页
scripts/feishu-cli.sh wiki node list \
  --space "7012345678901234567" \
  --page-size 50
```

响应示例：

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "space_id": "7012345678901234567",
        "node_token": "wikcnABCD1234",
        "obj_token": "doxcnEFGH5678",
        "obj_type": "docx",
        "parent_node_token": "",
        "node_type": "origin",
        "title": "产品需求文档"
      }
    ]
  }
}
```

- `node_token`：节点在 wiki 中的 token
- `obj_token`：文档/表格本身的 token（可用于 docx/sheets 操作）
- `obj_type`：节点类型（`docx`/`sheet`/`bitable`等）

### wiki node create — 新建节点（页面）

```bash
# 在根目录创建新 docx 页面
scripts/feishu-cli.sh wiki node create \
  --space "7012345678901234567" \
  --data '{"obj_type":"docx","parent_node_token":"","node_type":"origin","title":"新页面"}'

# 在某个节点下创建子页面
scripts/feishu-cli.sh wiki node create \
  --space "7012345678901234567" \
  --data '{"obj_type":"docx","parent_node_token":"wikcnXXXX1234","node_type":"origin","title":"子页面"}'

# 创建快捷方式（指向已存在的文档）
scripts/feishu-cli.sh wiki node create \
  --space "7012345678901234567" \
  --data '{"obj_type":"docx","parent_node_token":"","node_type":"shortcut","origin_node_token":"wikcnSRCNODE","title":"快捷方式名"}'
```

`node_type` 取值：
- `origin`：创建新文档
- `shortcut`：创建快捷方式

使用模板文件：

```bash
scripts/feishu-cli.sh wiki node create \
  --space "7012345678901234567" \
  --data @skills/feishu-cloud-docs/templates/wiki-node.json
```

### wiki node copy — 复制节点

```bash
scripts/feishu-cli.sh wiki node copy \
  --space "7012345678901234567" \
  --node "wikcnABCD1234" \
  --data '{"target_parent_token":"","target_space_id":"7012345678901234567"}'
```

### wiki node move — 移动节点

```bash
scripts/feishu-cli.sh wiki node move \
  --space "7012345678901234567" \
  --node "wikcnABCD1234" \
  --data '{"target_parent_token":"wikcnPARENT","target_space_id":"7012345678901234567"}'
```

---

## Member 操作

### wiki member list

```bash
scripts/feishu-cli.sh wiki member list --space "7012345678901234567"
```

### wiki member create — 添加成员

```bash
# member_type: userid / openid / unionid / email
# role: admin / member / full_access / edit / read
scripts/feishu-cli.sh wiki member create \
  --space "7012345678901234567" \
  --data '{"member_type":"openid","member_id":"ou_xxx","role":"edit"}'
```

### wiki member delete — 移除成员

```bash
scripts/feishu-cli.sh wiki member delete \
  --space "7012345678901234567" \
  --member-id "ou_xxx" \
  --data '{"member_type":"openid","member_id":"ou_xxx","role":"edit"}'
```

---

## Setting 操作

```bash
scripts/feishu-cli.sh wiki setting update \
  --space "7012345678901234567" \
  --data '{"create_setting":"admin","security_setting":"public","comment_setting":"allow"}'
```

---

## wiki search — 搜索节点

```bash
# 搜索关键词（v1 API）
scripts/feishu-cli.sh wiki search \
  --data '{"query":"产品需求"}' \
  --page-size 20
```

---

## 典型工作流：浏览知识库

```bash
CLI="scripts/feishu-cli.sh"

# 1. 列出所有空间，获取 space_id
$CLI wiki space list

# 假设 SPACE_ID=7012345678901234567

# 2. 列出根节点
$CLI wiki node list --space "7012345678901234567"

# 3. 列出某节点的子节点
$CLI wiki node list --space "7012345678901234567" --parent "wikcnABCD1234"
```

或使用封装脚本：

```bash
bash skills/feishu-cloud-docs/scripts/wiki-list-all.sh
```
