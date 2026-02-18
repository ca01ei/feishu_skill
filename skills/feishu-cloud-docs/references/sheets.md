# sheets 电子表格操作参考

## 概述

`sheets` 命令操作飞书电子表格（Spreadsheet）。

**Token 来源**：从 URL `https://xxx.feishu.cn/sheets/<spreadsheet_token>` 提取，用作 `--token`。

**层级结构**：
```
Spreadsheet（电子表格）  ← --token
  └── Sheet（工作表，页签）  ← --sheet-id
        ├── Filter（筛选）
        ├── FilterView（筛选视图）
        └── FloatImage（浮动图片）
```

**⚠️ 关键**：`sheet_id` 不在 URL 中，需通过 `sheets sheet list --token <token>` 获取。

---

## 命令速览

| 命令 | 说明 |
|------|------|
| `sheets create` | 新建电子表格 |
| `sheets get` | 获取电子表格元数据 |
| `sheets update` | 修改标题等属性 |
| `sheets sheet list` | **列出所有 Sheet 及其 ID**（最常用） |
| `sheets filter create/get/update/delete` | Sheet 筛选条件 CRUD |
| `sheets filter-view create/get/list/update/delete` | 筛选视图 CRUD |
| `sheets float-image create/get/list/update/delete` | 浮动图片 CRUD |

---

## sheets create — 新建电子表格

```bash
scripts/feishu-cli.sh sheets create --title "季度报表"
scripts/feishu-cli.sh sheets create --title "季度报表" --folder-token "fldcnXxx"
```

**返回关键字段**：`data.spreadsheet.spreadsheet_token`（后续所有命令的 `--token`）

---

## sheets get — 获取电子表格信息

```bash
scripts/feishu-cli.sh sheets get --token "shtcnABCD1234"
```

---

## sheets update — 修改属性

```bash
scripts/feishu-cli.sh sheets update --token "shtcnABCD1234" --title "新标题"
```

---

## sheets sheet list — 列出所有 Sheet（获取 sheet_id 的方法）

```bash
scripts/feishu-cli.sh sheets sheet list --token "shtcnABCD1234"
```

响应示例：

```json
{
  "success": true,
  "data": {
    "sheets": [
      {
        "sheet_id": "6e5c4d",
        "title": "Sheet1",
        "index": 0,
        "row_count": 1000,
        "column_count": 26
      },
      {
        "sheet_id": "7f8a3b",
        "title": "数据汇总",
        "index": 1
      }
    ]
  }
}
```

**`sheet_id` 就是后续 filter/filter-view/float-image 命令所需的 `--sheet-id`**。

也可使用封装脚本查看所有 sheet：

```bash
bash skills/feishu-cloud-docs/scripts/sheets-read-all.sh "shtcnABCD1234"
```

---

## sheets filter — Sheet 筛选条件

### filter create

```bash
scripts/feishu-cli.sh sheets filter create \
  --token "shtcnABCD1234" \
  --sheet-id "6e5c4d" \
  --data '{"range":"6e5c4d!A1:D10","col":"A","condition":{"filter_type":"number","parameter":["10"]}}'
```

### filter get

```bash
scripts/feishu-cli.sh sheets filter get \
  --token "shtcnABCD1234" \
  --sheet-id "6e5c4d"
```

### filter update

```bash
scripts/feishu-cli.sh sheets filter update \
  --token "shtcnABCD1234" \
  --sheet-id "6e5c4d" \
  --data '{"range":"6e5c4d!A1:D10","col":"B","condition":{"filter_type":"text","parameter":["完成"]}}'
```

### filter delete

```bash
scripts/feishu-cli.sh sheets filter delete \
  --token "shtcnABCD1234" \
  --sheet-id "6e5c4d"
```

---

## sheets filter-view — 筛选视图

```bash
# 创建
scripts/feishu-cli.sh sheets filter-view create \
  --token "shtcnABCD1234" \
  --sheet-id "6e5c4d" \
  --data '{"filter_view_name":"我的视图","range":"6e5c4d!A:D"}'

# 查询所有（获取 filter_view_id）
scripts/feishu-cli.sh sheets filter-view list \
  --token "shtcnABCD1234" \
  --sheet-id "6e5c4d"

# 获取单个
scripts/feishu-cli.sh sheets filter-view get \
  --token "shtcnABCD1234" \
  --sheet-id "6e5c4d" \
  --filter-view-id "fviewXxxx"

# 更新
scripts/feishu-cli.sh sheets filter-view update \
  --token "shtcnABCD1234" \
  --sheet-id "6e5c4d" \
  --filter-view-id "fviewXxxx" \
  --data '{"filter_view_name":"新视图名称"}'

# 删除
scripts/feishu-cli.sh sheets filter-view delete \
  --token "shtcnABCD1234" \
  --sheet-id "6e5c4d" \
  --filter-view-id "fviewXxxx"
```

---

## sheets float-image — 浮动图片

```bash
# 创建（需要先通过飞书 API 上传图片获取 image_token）
scripts/feishu-cli.sh sheets float-image create \
  --token "shtcnABCD1234" \
  --sheet-id "6e5c4d" \
  --data '{"float_image_token":"img_xxx","range":"6e5c4d!B2:D6","width":400,"height":300}'

# 列出所有
scripts/feishu-cli.sh sheets float-image list \
  --token "shtcnABCD1234" \
  --sheet-id "6e5c4d"

# 获取单个
scripts/feishu-cli.sh sheets float-image get \
  --token "shtcnABCD1234" \
  --sheet-id "6e5c4d" \
  --float-image-id "floatXxx"

# 更新
scripts/feishu-cli.sh sheets float-image update \
  --token "shtcnABCD1234" \
  --sheet-id "6e5c4d" \
  --float-image-id "floatXxx" \
  --data '{"width":500,"height":350}'

# 删除
scripts/feishu-cli.sh sheets float-image delete \
  --token "shtcnABCD1234" \
  --sheet-id "6e5c4d" \
  --float-image-id "floatXxx"
```

---

## 典型工作流：读取表格数据

```bash
CLI="scripts/feishu-cli.sh"
TOKEN="shtcnABCD1234"

# 1. 查看电子表格基本信息
$CLI sheets get --token "$TOKEN"

# 2. 列出所有 sheet，获取 sheet_id
$CLI sheets sheet list --token "$TOKEN"

# 3. 查看某个 sheet 的筛选视图
$CLI sheets filter-view list --token "$TOKEN" --sheet-id "6e5c4d"
```
