# bitable 多维表格操作参考

## 概述

`bitable` 命令操作飞书多维表格（Base/Bitable）。

**Token 来源**：从 URL `https://xxx.feishu.cn/base/<app_token>` 提取，用作 `--app-token`。

**层级结构**：

```
App（多维表格）         ← --app-token
  └── Table（数据表）   ← --table-id   （不在 URL 中，需先 list）
        ├── Record（记录行）  ← --record-id
        ├── Field（字段列）   ← --field-id
        └── View（视图）      ← --view-id
```

**⚠️ 关键**：`table_id` 不在 URL 中。必须先通过 `bitable table list` 获取。

---

## 命令速览

| 命令 | 说明 |
|------|------|
| `bitable create` | 新建多维表格 App |
| `bitable get` | 获取 App 信息 |
| `bitable update` | 修改 App 名称 |
| `bitable copy` | 复制 App |
| `bitable table list` | **列出所有数据表（获取 table_id）** |
| `bitable table create/delete/patch` | 数据表 CRUD |
| `bitable record list` | 列出记录（分页） |
| `bitable record get` | 获取单条记录 |
| `bitable record create` | **新建记录** |
| `bitable record update` | 更新记录 |
| `bitable record delete` | 删除记录 |
| `bitable field list` | 列出所有字段 |
| `bitable field create/update/delete` | 字段 CRUD |
| `bitable view list/get/create/delete` | 视图 CRUD |

---

## App 级别操作

### bitable create — 新建 App

```bash
scripts/feishu-cli.sh bitable create --name "项目管理表"
scripts/feishu-cli.sh bitable create --name "项目管理表" --folder-token "fldcnXxx"
```

**返回关键字段**：`data.app.app_token`

### bitable get — 获取 App 信息

```bash
scripts/feishu-cli.sh bitable get --app-token "bascnABCD1234"
```

### bitable update — 修改名称

```bash
scripts/feishu-cli.sh bitable update --app-token "bascnABCD1234" --name "新名称"
```

### bitable copy — 复制 App

```bash
scripts/feishu-cli.sh bitable copy --app-token "bascnABCD1234" --name "副本名称"
scripts/feishu-cli.sh bitable copy --app-token "bascnABCD1234" \
  --name "副本名称" --folder-token "fldcnXxx"
```

---

## Table 级别操作

### bitable table list — 列出数据表（获取 table_id 的方法）

```bash
scripts/feishu-cli.sh bitable table list --app-token "bascnABCD1234"
```

响应示例：

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "table_id": "tblXXXX1111",
        "name": "任务列表",
        "revision": 5
      },
      {
        "table_id": "tblXXXX2222",
        "name": "人员信息"
      }
    ]
  }
}
```

### bitable table create

```bash
scripts/feishu-cli.sh bitable table create \
  --app-token "bascnABCD1234" \
  --name "新数据表"
```

### bitable table patch — 重命名

```bash
scripts/feishu-cli.sh bitable table patch \
  --app-token "bascnABCD1234" \
  --table-id "tblXXXX1111" \
  --name "重命名后的表"
```

### bitable table delete

```bash
scripts/feishu-cli.sh bitable table delete \
  --app-token "bascnABCD1234" \
  --table-id "tblXXXX1111"
```

---

## Record 级别操作（最常用）

### bitable record list

```bash
# 基本列出（默认 20 条）
scripts/feishu-cli.sh bitable record list \
  --app-token "bascnABCD1234" \
  --table-id "tblXXXX1111"

# 指定分页
scripts/feishu-cli.sh bitable record list \
  --app-token "bascnABCD1234" \
  --table-id "tblXXXX1111" \
  --page-size 50 \
  --page-token "xxx"
```

响应示例：

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "record_id": "recXXXX0001",
        "fields": {
          "任务名称": "修复 Bug",
          "状态": "进行中",
          "负责人": [{"id": "ou_xxx", "name": "张三"}]
        }
      }
    ],
    "has_more": false
  }
}
```

### bitable record get

```bash
scripts/feishu-cli.sh bitable record get \
  --app-token "bascnABCD1234" \
  --table-id "tblXXXX1111" \
  --record-id "recXXXX0001"
```

### bitable record create — 新建记录

```bash
# --fields 接受 JSON 对象，键名必须与实际字段名完全一致
scripts/feishu-cli.sh bitable record create \
  --app-token "bascnABCD1234" \
  --table-id "tblXXXX1111" \
  --fields '{"任务名称":"新任务","状态":"待处理"}'

# 使用模板文件
scripts/feishu-cli.sh bitable record create \
  --app-token "bascnABCD1234" \
  --table-id "tblXXXX1111" \
  --fields @skills/feishu-cloud-docs/templates/bitable-record.json
```

**⚠️ 注意**：`--fields` 直接接受字段键值对，不需要包装在 `{"fields": {...}}` 外层。

**返回关键字段**：`data.record.record_id`

### bitable record update

```bash
scripts/feishu-cli.sh bitable record update \
  --app-token "bascnABCD1234" \
  --table-id "tblXXXX1111" \
  --record-id "recXXXX0001" \
  --fields '{"状态":"已完成","备注":"已验收"}'
```

### bitable record delete

```bash
scripts/feishu-cli.sh bitable record delete \
  --app-token "bascnABCD1234" \
  --table-id "tblXXXX1111" \
  --record-id "recXXXX0001"
```

---

## Field 级别操作

### bitable field list — 列出所有字段（查看字段名和类型）

```bash
scripts/feishu-cli.sh bitable field list \
  --app-token "bascnABCD1234" \
  --table-id "tblXXXX1111"
```

响应中的 `field_name` 就是 record create/update 时 `--fields` JSON 的键名。

### bitable field create

```bash
scripts/feishu-cli.sh bitable field create \
  --app-token "bascnABCD1234" \
  --table-id "tblXXXX1111" \
  --field-name "优先级" \
  --field-type 3
# field-type: 1=文本 2=数字 3=单选 4=多选 5=日期 7=复选框 11=人员 15=URL
# 完整类型列表见 templates/bitable-field-types.json
```

### bitable field update

```bash
scripts/feishu-cli.sh bitable field update \
  --app-token "bascnABCD1234" \
  --table-id "tblXXXX1111" \
  --field-id "fldXXXX0001" \
  --field-name "新字段名" \
  --field-type 1
```

### bitable field delete

```bash
scripts/feishu-cli.sh bitable field delete \
  --app-token "bascnABCD1234" \
  --table-id "tblXXXX1111" \
  --field-id "fldXXXX0001"
```

---

## View 级别操作

### bitable view list

```bash
scripts/feishu-cli.sh bitable view list \
  --app-token "bascnABCD1234" \
  --table-id "tblXXXX1111"
```

### bitable view get

```bash
scripts/feishu-cli.sh bitable view get \
  --app-token "bascnABCD1234" \
  --table-id "tblXXXX1111" \
  --view-id "vewXXXX0001"
```

### bitable view create

```bash
# view_type: grid(表格) / kanban(看板) / gallery(画册) / gantt(甘特) / form(表单)
scripts/feishu-cli.sh bitable view create \
  --app-token "bascnABCD1234" \
  --table-id "tblXXXX1111" \
  --view-name "我的看板" \
  --view-type "kanban"
```

### bitable view delete

```bash
scripts/feishu-cli.sh bitable view delete \
  --app-token "bascnABCD1234" \
  --table-id "tblXXXX1111" \
  --view-id "vewXXXX0001"
```

---

## 典型工作流：CRUD 完整演示

```bash
CLI="scripts/feishu-cli.sh"
APP_TOKEN="bascnABCD1234"

# 1. 获取 table_id（必须先执行）
$CLI bitable table list --app-token "$APP_TOKEN"

# 假设得到 TABLE_ID=tblXXXX1111

# 2. 查看字段结构（了解字段名）
$CLI bitable field list --app-token "$APP_TOKEN" --table-id "tblXXXX1111"

# 3. 创建记录
CREATE=$($CLI bitable record create \
  --app-token "$APP_TOKEN" \
  --table-id "tblXXXX1111" \
  --fields '{"任务名称":"Test","状态":"待处理"}')
RECORD_ID=$(echo "$CREATE" | python3 -c "import json,sys; print(json.load(sys.stdin)['data']['record']['record_id'])")

# 4. 更新记录
$CLI bitable record update \
  --app-token "$APP_TOKEN" \
  --table-id "tblXXXX1111" \
  --record-id "$RECORD_ID" \
  --fields '{"状态":"已完成"}'

# 5. 删除记录
$CLI bitable record delete \
  --app-token "$APP_TOKEN" \
  --table-id "tblXXXX1111" \
  --record-id "$RECORD_ID"
```

或使用封装脚本：

```bash
bash skills/feishu-cloud-docs/scripts/bitable-full-crud.sh "bascnABCD1234" "tblXXXX1111"
```
