# 模型 (Model) 实体

## 定义

模型信息用于记录提示词使用的 AI 模型。

## 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| name | string | 模型名称 |
| type | PromptType (enum) | 适用类型 |
| provider | string | 提供商 |
| description | string | 模型描述 |
| parameters | JSON | 模型参数配置 |
| created_at | datetime | 创建时间 |

## 业务规则

- name 长度限制：最大 100 字符
- name + type 组合唯一
- provider 长度限制：最大 100 字符