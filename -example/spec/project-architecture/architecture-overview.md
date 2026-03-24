# 架构概览

## 系统架构

采用 DDD (领域驱动设计) 四层架构：

```
┌─────────────────────────────────────────┐
│           Presentation Layer            │
│         (API/Routers 层)                 │
├─────────────────────────────────────────┤
│           Application Layer             │
│         (Application Services)          │
├─────────────────────────────────────────┤
│             Domain Layer                │
│     (Entities, Value Objects,           │
│      Domain Services, Repositories)     │
├─────────────────────────────────────────┤
│         Infrastructure Layer            │
│   (SQLAlchemy Repositories,             │
│    File Storage, Migrations)            │
└─────────────────────────────────────────┘
```

## 核心模块

### V1.0 基础模块
1. **Prompt (提示词)**: 核心业务实体
2. **Category (分类)**: 提示词分类
3. **Tag (标签)**: 提示词标签
4. **Model (模型)**: 模型信息管理
5. **Attachment (附件)**: 图片/视频附件

### V2.0 新增模块
6. **Template (模板)**: 提示词模板，支持变量占位符
7. **Workflow (工作流)**: 多步骤工作流编排
8. **WorkflowExecution (执行记录)**: 工作流执行历史
9. **ImportExport (导入导出)**: 批量数据处理服务

## 目录结构

```
app/
├── api/              # API 路由层
├── application/      # 应用服务层
│   └── services/     # 业务服务
├── domain/           # 领域层
│   ├── entities/     # 实体
│   ├── value_objects # 值对象
│   ├── repositories # 仓储接口
│   └── services/     # 领域服务
│       ├── template_service.py      # 模板变量解析
│       └── workflow_engine.py       # 工作流执行引擎
├── infrastructure/   # 基础设施层
│   ├── persistence/  # 持久化实现
│   ├── storage/      # 文件存储
│   └── exporters/    # 导出器实现
│       ├── json_exporter.py
│       ├── csv_exporter.py
│       └── markdown_exporter.py
└── main.py          # 应用入口
```

## 模块依赖关系

```
Workflow ──┬──> Template ──> Prompt
           │
           └──> Prompt

Template ──> Category
          ──> Model

WorkflowExecution ──> Workflow
```

## 领域服务

### TemplateService
- `parse_variables(content)` - 解析模板中的变量
- `validate_variables(template)` - 验证变量定义
- `instantiate(template, values)` - 生成提示词内容

### WorkflowEngine
- `execute(workflow, inputs)` - 执行工作流
- `validate_workflow(workflow)` - 验证工作流定义
- `resolve_step_inputs(step, context)` - 解析步骤输入

### ImportExportService
- `export_prompts(format, filters)` - 导出提示词
- `import_prompts(format, data)` - 导入提示词
- `export_templates(format, filters)` - 导出模板