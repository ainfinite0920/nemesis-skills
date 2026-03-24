# 分类 (Category) 实体

## 定义

分类用于对提示词进行组织管理。

## 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| name | string | 分类名称 |
| type | PromptType (enum) | 所属提示词类型 |
| description | string | 分类描述 |
| parent_id | UUID | 父分类ID |
| created_at | datetime | 创建时间 |

## 业务规则

- name 长度限制：最大 100 字符
- 同一类型下分类名称不能重复
- 支持二级分类（parent_id 为空表示一级分类）
- 删除分类时，子分类一并处理