# 模板 (Template) 实体

## 定义

模板是可复用的提示词蓝图，支持变量占位符，用于快速生成结构化的提示词。

## 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| title | string | 模板标题 |
| content | string | 模板内容（含变量占位符） |
| type | PromptType (enum) | 提示词类型：image/video/code |
| category_id | UUID | 所属分类 |
| variables | JSON | 变量定义列表 |
| description | string | 模板描述 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

## 变量定义结构

```json
{
  "variables": [
    {
      "name": "style",
      "type": "select",
      "label": "风格",
      "required": true,
      "default": "写实",
      "options": ["写实", "卡通", "油画", "水彩"],
      "description": "图片生成风格"
    },
    {
      "name": "subject",
      "type": "text",
      "label": "主题",
      "required": true,
      "default": null,
      "description": "图片主体内容"
    }
  ]
}
```

## 变量类型

| 类型 | 说明 | 参数 |
|------|------|------|
| text | 文本输入 | min_length, max_length |
| number | 数字输入 | min, max, step |
| select | 下拉选择 | options (必需) |
| boolean | 布尔值 | 无 |

## 业务规则

- 变量名只能包含字母、数字、下划线
- 变量名在模板内唯一
- 占位符语法：`{{变量名}}`
- content 中引用的变量必须在 variables 中定义
- 从模板创建提示词时，必须提供所有 required 变量的值

## 关联关系

- 一个模板属于一个分类（可选）
- 模板可以被多个工作流步骤引用

## 行为

### instantiate(variables: dict) -> str
根据提供的变量值，生成最终的提示词内容。

**逻辑：**
1. 验证所有 required 变量是否提供
2. 合并默认值
3. 替换占位符
4. 返回生成的内容

### validate() -> bool
验证模板内容中的变量引用是否与 variables 定义一致。