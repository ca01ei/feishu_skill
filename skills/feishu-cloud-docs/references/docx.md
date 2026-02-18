# docx 文档操作参考

## 概述

`docx` 命令操作**新版飞书文档**（URL 中含 `/docx/`）。旧版文档请用 `docs get`（只读）。

**Token 来源**：从 URL `https://xxx.feishu.cn/docx/<document_id>` 提取 `document_id`，用作 `--token`。

---

## 命令速览

| 命令 | 说明 |
|------|------|
| `docx create` | 新建文档（返回 document_id） |
| `docx get` | 获取文档元数据（标题、版本等） |
| `docx content` | **获取文档全文**（最常用读取方式） |
| `docx block list` | 列出所有块（分页，首块是根块） |
| `docx block get` | 获取单个块内容 |
| `docx block create` | **写入内容块**（最常用写入方式） |
| `docx block delete` | 按索引范围删除子块 |

---

## docx create — 新建文档

```bash
# 基本创建
scripts/feishu-cli.sh docx create --title "我的文档"

# 指定父文件夹（folder_token 从网盘 URL 提取）
scripts/feishu-cli.sh docx create --title "我的文档" --folder-token "fldcnXxxxx"
```

**返回关键字段**：`data.document.document_id`（即后续所有命令的 `--token`）

响应示例：

```json
{
  "success": true,
  "data": {
    "document": {
      "document_id": "doxcnABCD1234",
      "revision_id": 1,
      "title": "我的文档"
    }
  }
}
```

---

## docx get — 获取元数据

```bash
scripts/feishu-cli.sh docx get --token "doxcnABCD1234"
```

返回文档标题、版本号、创建/修改时间等。

---

## docx content — 获取全文内容（推荐读取方式）

```bash
# 默认语言
scripts/feishu-cli.sh docx content --token "doxcnABCD1234"

# 指定语言（0=默认 1=中文 2=英文 3=日文）
scripts/feishu-cli.sh docx content --token "doxcnABCD1234" --lang 0
```

返回的 `data.content` 字段包含纯文本内容，比逐块读取更高效。

---

## docx block list — 列出所有块

```bash
scripts/feishu-cli.sh docx block list --token "doxcnABCD1234"

# 分页（大文档）
scripts/feishu-cli.sh docx block list --token "doxcnABCD1234" --page-size 50
scripts/feishu-cli.sh docx block list --token "doxcnABCD1234" --page-size 50 --page-token "xxx"
```

**⚠️ 关键**：返回列表中第一个块（index 0）是文档**根块**（`block_type=1`，即 page block）。
写入新内容时，`--block-id` 应使用根块的 `block_id`，除非要在特定位置插入。

响应示例：

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "block_id": "doxcnABCD1234",
        "block_type": 1,
        "children": ["doxcnXXXX0001", "doxcnXXXX0002"]
      },
      {
        "block_id": "doxcnXXXX0001",
        "block_type": 2,
        "text": { "elements": [{"text_run": {"content": "Hello"}}] }
      }
    ],
    "page_token": "",
    "has_more": false
  }
}
```

---

## docx block get — 获取单个块

```bash
scripts/feishu-cli.sh docx block get \
  --token "doxcnABCD1234" \
  --block-id "doxcnXXXX0001"
```

---

## docx block create — 写入内容块（最常用！）

```bash
scripts/feishu-cli.sh docx block create \
  --token "doxcnABCD1234" \
  --block-id "<父块ID，通常是根块>" \
  --data '<json_payload>'
```

**参数说明**：
- `--block-id`：新块插入到该块的子节点末尾
- `--data`：JSON 格式的块数据，见下方格式说明

### 写入文本段落（最常用）

```bash
scripts/feishu-cli.sh docx block create \
  --token "doxcnABCD1234" \
  --block-id "doxcnABCD1234" \
  --data '{"children":[{"block_type":2,"text":{"elements":[{"text_run":{"content":"Hello World","text_element_style":{}}}],"style":{}}}]}'
```

使用模板文件（推荐，避免 JSON 格式错误）：

```bash
# 先修改模板文件中的文本内容，再使用
scripts/feishu-cli.sh docx block create \
  --token "doxcnABCD1234" \
  --block-id "doxcnABCD1234" \
  --data @skills/feishu-cloud-docs/templates/docx-block-text.json
```

### 写入代码块

```bash
scripts/feishu-cli.sh docx block create \
  --token "doxcnABCD1234" \
  --block-id "doxcnABCD1234" \
  --data @skills/feishu-cloud-docs/templates/docx-block-code.json
```

### block create JSON 格式说明

```json
{
  "children": [
    {
      "block_type": 2,
      "text": {
        "elements": [
          {
            "text_run": {
              "content": "在这里填写文本内容",
              "text_element_style": {}
            }
          }
        ],
        "style": {}
      }
    }
  ]
}
```

**block_type 常用值**：

| block_type | 含义 | 字段名 |
|-----------|------|--------|
| 1 | 文档根块（page block，只有一个） | - |
| 2 | 文本段落 | `text` |
| 3 | 一级标题 | `heading1` |
| 4 | 二级标题 | `heading2` |
| 5 | 三级标题 | `heading3` |
| 6 | 四级标题 | `heading4` |
| 7 | 五级标题 | `heading5` |
| 12 | 无序列表 | `bullet` |
| 13 | 有序列表 | `ordered` |
| 14 | 代码块 | `code` |
| 15 | 引用 | `quote` |
| 22 | 代码块（新版） | `code` |
| 27 | 表格 | `table` |

**代码块语言 ID（`style.language`）**：

| ID | 语言 | ID | 语言 |
|----|------|----|------|
| 1 | PlainText | 49 | Python |
| 4 | C | 50 | JavaScript |
| 5 | C++ | 51 | TypeScript |
| 10 | Go | 48 | Java |
| 18 | Shell/Bash | 46 | SQL |
| 24 | Kotlin | 56 | Rust |

---

## docx block delete — 删除子块

按索引范围删除父块的子块（start 含，end 不含）：

```bash
# 删除根块下第 0 个子块
scripts/feishu-cli.sh docx block delete \
  --token "doxcnABCD1234" \
  --block-id "<父块ID>" \
  --start-index 0 \
  --end-index 1

# 删除前 3 个子块
scripts/feishu-cli.sh docx block delete \
  --token "doxcnABCD1234" \
  --block-id "<父块ID>" \
  --start-index 0 \
  --end-index 3
```

---

## 多步骤示例：创建文档并写入内容

```bash
CLI="scripts/feishu-cli.sh"

# 1. 创建文档
CREATE=$($CLI docx create --title "My Doc")
DOC_TOKEN=$(echo "$CREATE" | python3 -c "import json,sys; print(json.load(sys.stdin)['data']['document']['document_id'])")
echo "Document token: $DOC_TOKEN"

# 2. 获取根块 ID
BLOCKS=$($CLI docx block list --token "$DOC_TOKEN")
ROOT_ID=$(echo "$BLOCKS" | python3 -c "import json,sys; print(json.load(sys.stdin)['data']['items'][0]['block_id'])")
echo "Root block ID: $ROOT_ID"

# 3. 写入文本段落
$CLI docx block create \
  --token "$DOC_TOKEN" \
  --block-id "$ROOT_ID" \
  --data '{"children":[{"block_type":2,"text":{"elements":[{"text_run":{"content":"Hello!","text_element_style":{}}}],"style":{}}}]}'
```

或直接使用封装脚本：

```bash
bash skills/feishu-cloud-docs/scripts/docx-create-and-write.sh "My Doc" "Hello World"
```
