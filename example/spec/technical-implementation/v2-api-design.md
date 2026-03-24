# V2.0 技术实现规格

## 数据库新增表

### templates (模板表)
```sql
CREATE TABLE templates (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('image', 'video', 'code')),
    category_id TEXT,
    variables JSON NOT NULL DEFAULT '[]',
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);
```

### workflows (工作流表)
```sql
CREATE TABLE workflows (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    type TEXT NOT NULL CHECK(type IN ('image', 'video', 'code')),
    steps JSON NOT NULL DEFAULT '[]',
    status TEXT DEFAULT 'draft' CHECK(status IN ('draft', 'active', 'archived')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### workflow_executions (工作流执行记录表)
```sql
CREATE TABLE workflow_executions (
    id TEXT PRIMARY KEY,
    workflow_id TEXT NOT NULL,
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    inputs JSON,
    outputs JSON,
    step_executions JSON DEFAULT '[]',
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workflow_id) REFERENCES workflows(id)
);
```

## 新增 API 设计

### 模板 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/templates | 获取模板列表 |
| GET | /api/templates/{id} | 获取模板详情 |
| POST | /api/templates | 创建模板 |
| PUT | /api/templates/{id} | 更新模板 |
| DELETE | /api/templates/{id} | 删除模板 |
| POST | /api/templates/{id}/instantiate | 从模板生成提示词 |
| POST | /api/templates/{id}/validate | 验证模板变量 |

### 导入导出 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/export | 导出提示词 |
| POST | /api/import | 导入提示词 |
| GET | /api/export/templates | 导出模板 |
| GET | /api/import/template | 下载导入模板 |

导出参数：
- `format`: json/csv/markdown
- `prompt_ids`: 指定提示词ID列表（可选）
- `category_id`: 按分类导出（可选）
- `tag_ids`: 按标签导出（可选）

### 工作流 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/workflows | 获取工作流列表 |
| GET | /api/workflows/{id} | 获取工作流详情 |
| POST | /api/workflows | 创建工作流 |
| PUT | /api/workflows/{id} | 更新工作流 |
| DELETE | /api/workflows/{id} | 删除工作流 |
| POST | /api/workflows/{id}/execute | 执行工作流 |
| GET | /api/workflows/{id}/executions | 获取执行历史 |
| GET | /api/executions/{id} | 获取执行详情 |
| POST | /api/executions/{id}/cancel | 取消执行 |
| POST | /api/executions/{id}/retry | 重试执行 |

## 导入导出格式

### JSON 格式
```json
{
  "version": "2.0",
  "exported_at": "2026-03-20T10:00:00Z",
  "prompts": [
    {
      "title": "示例提示词",
      "content": "...",
      "type": "image",
      "category": "自然风光",
      "tags": ["风景"],
      "model": "DALL-E 3"
    }
  ],
  "templates": [...],
  "categories": [...],
  "tags": [...],
  "models": [...]
}
```

### CSV 格式
```csv
title,content,type,category,tags,model,description
"日落","一张日落照片",image,"自然风光","风景,日落","DALL-E 3","美丽的日落"
```

### Markdown 格式
```markdown
# 提示词：日落

- **类型**: image
- **分类**: 自然风光
- **标签**: 风景, 日落
- **模型**: DALL-E 3

## 内容

一张美丽的日落照片...
```

## 变量解析引擎

### 占位符语法
- `{{variable_name}}` - 基础变量
- `{{step_id.output_name}}` - 跨步骤引用

### 解析流程
1. 提取所有 `{{...}}` 占位符
2. 验证变量定义完整性
3. 合并用户输入与默认值
4. 执行变量替换
5. 返回最终内容