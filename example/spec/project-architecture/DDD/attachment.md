# 附件 (Attachment) 实体

## 定义

附件用于存储提示词关联的图片和视频文件。

## 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| prompt_id | UUID | 所属提示词ID |
| file_path | string | 文件存储路径 |
| file_name | string | 原始文件名 |
| file_type | AttachmentType (enum) | 文件类型：image/video |
| mime_type | string | MIME类型 |
| file_size | int | 文件大小（字节） |
| created_at | datetime | 上传时间 |

## 业务规则

- 支持的图片格式：jpg, jpeg, png, gif, webp
- 支持的视频格式：mp4, webm, mov
- 单个文件大小限制：100MB
- 文件存储在本地 uploads 目录

## 关联关系

- 一个附件属于一个提示词
- 删除提示词时，附件一并删除