# 工作流执行记录 (WorkflowExecution) 实体

## 定义

记录工作流的每次执行历史，包含执行状态、输入输出、日志等信息。

## 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| workflow_id | UUID | 所属工作流ID |
| status | ExecutionStatus (enum) | 执行状态 |
| inputs | JSON | 执行输入参数 |
| outputs | JSON | 执行输出结果 |
| started_at | datetime | 开始时间 |
| completed_at | datetime | 完成时间 |
| created_at | datetime | 创建时间 |

## 执行状态

| 状态 | 说明 |
|------|------|
| pending | 待执行 |
| running | 执行中 |
| completed | 已完成 |
| failed | 失败 |
| cancelled | 已取消 |

## 步骤执行记录

每次执行包含多个步骤执行记录：

```json
{
  "step_executions": [
    {
      "step_id": "step_1",
      "status": "completed",
      "started_at": "2026-03-20T10:00:00Z",
      "completed_at": "2026-03-20T10:00:05Z",
      "inputs": {...},
      "outputs": {"outline": "..."},
      "error": null
    },
    {
      "step_id": "step_2",
      "status": "running",
      "started_at": "2026-03-20T10:00:05Z",
      "completed_at": null,
      "inputs": {...},
      "outputs": null,
      "error": null
    }
  ]
}
```

## 业务规则

- 执行记录不可修改，只能追加
- 失败时记录错误信息
- 支持重新执行（创建新的执行记录）

## 关联关系

- 一个执行记录属于一个工作流