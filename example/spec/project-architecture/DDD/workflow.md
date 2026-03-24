# 工作流 (Workflow) 实体

## 定义

工作流是多步骤提示词执行流程的编排，支持步骤间的变量传递和顺序控制。

## 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| name | string | 工作流名称 |
| description | string | 工作流描述 |
| type | PromptType (enum) | 工作流类型 |
| steps | JSON | 步骤定义列表 |
| status | WorkflowStatus (enum) | 状态：draft/active/archived |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

## 步骤定义结构

```json
{
  "steps": [
    {
      "id": "step_1",
      "name": "生成文章大纲",
      "type": "template",
      "template_id": "uuid-xxx",
      "prompt_id": null,
      "inputs": {},
      "outputs": ["outline"],
      "order": 1,
      "condition": null,
      "on_failure": "stop"
    },
    {
      "id": "step_2",
      "name": "生成配图提示词",
      "type": "template",
      "template_id": "uuid-yyy",
      "inputs": {
        "context": "{{step_1.outline}}"
      },
      "outputs": ["image_prompt"],
      "order": 2,
      "condition": null,
      "on_failure": "skip"
    },
    {
      "id": "step_3",
      "name": "生成配图",
      "type": "prompt",
      "prompt_id": "uuid-zzz",
      "inputs": {
        "content": "{{step_2.image_prompt}}"
      },
      "outputs": [],
      "order": 3,
      "condition": null,
      "on_failure": "stop"
    }
  ]
}
```

## 步骤类型

| 类型 | 说明 | 必需参数 |
|------|------|----------|
| template | 基于模板执行 | template_id |
| prompt | 执行指定提示词 | prompt_id |
| transform | 数据转换处理 | transform_config |

## 执行状态

| 状态 | 说明 |
|------|------|
| draft | 草稿 |
| active | 激活可用 |
| archived | 已归档 |

## 失败处理策略

| 策略 | 说明 |
|------|------|
| stop | 停止整个工作流 |
| skip | 跳过当前步骤继续 |
| retry | 重试当前步骤 |

## 变量传递语法

- `{{step_id.output_name}}` - 引用上一步的输出
- `{{workflow.input_name}}` - 引用工作流输入参数

## 业务规则

- 步骤 order 必须唯一且连续
- 步骤间变量引用必须有效（引用的步骤必须存在且先执行）
- 删除模板/提示词时，检查是否被工作流引用

## 关联关系

- 工作流步骤可引用模板
- 工作流步骤可引用提示词