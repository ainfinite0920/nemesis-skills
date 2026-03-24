# 提示词 (Prompt) 实体

## 定义

提示词是系统的核心实体，代表用户创建的 AI 提示词。

## 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| content | string | 提示词内容 |
| type | PromptType (enum) | 提示词类型：image/video/code |
| category_id | UUID | 所属分类 |
| model_id | UUID | 使用的模型 |
| title | string | 标题 |
| description | string | 描述 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

## 业务规则

- content 长度限制：最大 10000 字符
- title 长度限制：最大 200 字符
- 同一分类下标题不能重复
- 删除分类时，该分类下的提示词不删除，但 category_id 设为 null

## 关联关系

- 一个提示词属于一个分类
- 一个提示词可以使用一个模型
- 一个提示词可以有多个标签
- 一个提示词可以有多个附件