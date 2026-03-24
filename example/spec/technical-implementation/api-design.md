# 技术实现规格

## 数据库设计

### 表结构

#### prompts (提示词表)
```sql
CREATE TABLE prompts (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('image', 'video', 'code')),
    category_id TEXT,
    model_id TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id),
    FOREIGN KEY (model_id) REFERENCES models(id)
);
```

#### categories (分类表)
```sql
CREATE TABLE categories (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('image', 'video', 'code')),
    description TEXT,
    parent_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES categories(id)
);
```

#### tags (标签表)
```sql
CREATE TABLE tags (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    color TEXT DEFAULT '#3B82F6',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### prompt_tags (提示词标签关联表)
```sql
CREATE TABLE prompt_tags (
    prompt_id TEXT NOT NULL,
    tag_id TEXT NOT NULL,
    PRIMARY KEY (prompt_id, tag_id),
    FOREIGN KEY (prompt_id) REFERENCES prompts(id),
    FOREIGN KEY (tag_id) REFERENCES tags(id)
);
```

#### models (模型表)
```sql
CREATE TABLE models (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('image', 'video', 'code')),
    provider TEXT NOT NULL,
    description TEXT,
    parameters JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, type)
);
```

#### attachments (附件表)
```sql
CREATE TABLE attachments (
    id TEXT PRIMARY KEY,
    prompt_id TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_type TEXT NOT NULL CHECK(file_type IN ('image', 'video')),
    mime_type TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (prompt_id) REFERENCES prompts(id) ON DELETE CASCADE
);
```

## API 设计

### 提示词 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/prompts | 获取提示词列表（支持搜索） |
| GET | /api/prompts/{id} | 获取提示词详情 |
| POST | /api/prompts | 创建提示词 |
| PUT | /api/prompts/{id} | 更新提示词 |
| DELETE | /api/prompts/{id} | 删除提示词 |
| POST | /api/prompts/{id}/tags | 添加标签 |
| DELETE | /api/prompts/{id}/tags/{tag_id} | 移除标签 |
| POST | /api/prompts/{id}/attachments | 上传附件 |
| DELETE | /api/prompts/{id}/attachments/{attachment_id} | 删除附件 |

### 分类 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/categories | 获取分类列表 |
| GET | /api/categories/{id} | 获取分类详情 |
| POST | /api/categories | 创建分类 |
| PUT | /api/categories/{id} | 更新分类 |
| DELETE | /api/categories/{id} | 删除分类 |

### 标签 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/tags | 获取标签列表 |
| POST | /api/tags | 创建标签 |
| PUT | /api/tags/{id} | 更新标签 |
| DELETE | /api/tags/{id} | 删除标签 |

### 模型 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/models | 获取模型列表 |
| GET | /api/models/{id} | 获取模型详情 |
| POST | /api/models | 创建模型 |
| PUT | /api/models/{id} | 更新模型 |
| DELETE | /api/models/{id} | 删除模型 |

### 搜索 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/search | 搜索提示词 |

搜索参数：
- `q`: 关键词（搜索内容）
- `type`: 提示词类型
- `category_id`: 分类ID
- `tag_ids`: 标签ID列表（逗号分隔）
- `model_id`: 模型ID
- `page`: 页码
- `page_size`: 每页数量