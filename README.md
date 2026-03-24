# nemesis-coding

> Signature Concept: Business-Technical Lockstep
> 先把业务设计、项目架构、代码实现、测试验证、迭代迁移锁进同一条演化链，再允许 AI 编码。

nemesis-coding 是一个面向 GitHub 协作、后端项目和后端模块演进的 spec-first coding skill。

它不是“更会写代码的提示词”，而是一个强约束工作流：

- 先建立可执行 spec 基线
- 再进入实现
- 实现同时绑定测试和迁移记录
- 用追加式 spec-migrations 追踪业务历史

它最独特的地方不是 DDD，也不是写 migration，而是上面的签名概念：
Business-Technical Lockstep。

也就是：业务、架构、代码、测试、迁移，不允许各自漂移。

## Why This Skill Exists

很多 AI 编码流程的问题，不是“代码写错了”，而是下面这些事情脱节了：

- 需求文档和代码已经不是一回事
- 架构说明停留在 PPT，代码按作者习惯乱长
- 测试是事后补的，覆盖不到真实业务约束
- 每次迭代只改代码，没有留下业务变更历史

nemesis-coding 的目标，就是把这几件事强制绑在一起。

## What Makes It Different

### 1. Spec Before Code

它不允许“先写点代码再补文档”。

不管是模糊需求还是详细需求，第一步都必须先形成可审批的 spec 基线。

### 2. Migration Before Implementation

它要求每次业务迭代先起草一条 spec-migration，再开始实现。

这意味着 migration 不是事后总结，而是编码前就存在的业务约束。

### 3. Append-Only Business History

旧的 migration 默认不能静默修改。

如果发现历史记录不准，要通过新增 migration 修正，而不是覆盖历史。

### 4. Tests Are Part of Delivery

新功能必须有单元测试。

跨层变更必须再补集成测试或 API 测试。

如果没有测试，这项工作默认不算完成。

### 5. Critical Gap Stop Mechanism

只要业务规则、聚合职责、API 契约、权限语义、测试验收标准等关键部分不清楚，就必须暂停编码，先修 spec。

## Best Fit

这个 skill 适合：

- 从模糊需求出发，先生成完整 spec，再推进实现的项目
- 已有旧 docs、旧 migration、旧代码，需要重组为活动 spec 基线的项目
- 重视业务可追溯性、架构稳定性和后续 AI 可维护性的后端系统
- 想把 AI 从“代码生成器”变成“规范驱动实现者”的团队

## Not a Good Fit

这个 skill 不适合：

- 前端页面和纯视觉设计工作
- 纯部署、纯运维、纯 IaC 任务
- 一次性脚本或快速原型
- 不愿意做 spec 审批、测试和迁移记录的轻量型修改

## Core Contract

nemesis-coding 不是默认模式，必须显式调用。

一旦使用，就默认接受以下合同：

1. 先 spec，后代码
2. 先 migration，后实现
3. 新功能必须带测试
4. 历史迁移追加记录，不静默改旧历史
5. 发现关键缺口或业务漂移时必须暂停

## Fixed Spec Layout

```text
spec/
  business-design/
  technical-implementation/
  project-architecture/
    DDD/
    tech-stack.md
    architecture-overview.md
  spec-migrations/
```

最小可启动条件：

- `spec/business-design/`
- `spec/technical-implementation/`
- `spec/project-architecture/`

完整关闭条件：

- `spec/spec-migrations/`
- 已回填的本次 migration
- 对应测试

## Workflow

```text
Discover legacy docs
-> Build or repair active spec baseline
-> Classify gaps
-> Approval gate
-> Draft new spec-migration
-> Implement code
-> Add tests
-> Run validation
-> Backfill migration with real impact
```

## Two Entry Modes

### Fuzzy Requirement Programming

适用于只有业务意图、还没有完整 spec 的场景。

流程：

1. 生成完整但粗粒度的 spec 初稿
2. 让用户修订和确认
3. 批准后再进入实现

### Detailed Requirement Programming

适用于已经有部分文档、部分代码、部分历史记录的场景。

流程：

1. 审计现有 spec、旧 docs 和旧 migrations
2. 将可用事实整合进固定 spec 树
3. 非关键缺口允许 AI 补全并显式列出假设
4. 关键缺口暂停，等待用户澄清

## What Counts as a Critical Gap

以下内容不清楚时，禁止继续编码：

- 业务规则和状态流转
- DDD 边界、聚合职责、实体关系
- API 契约和输入输出语义
- 持久化约束
- 权限和鉴权规则
- 测试验收标准
- 本次 migration 的业务目标和影响范围
- 外部依赖副作用

## Testing Policy

- 每个新功能都必须有单元测试
- 跨层改动必须补至少一类集成测试或 API 测试
- 如果环境允许，应运行真实测试或等效验证命令
- migration 的验证部分应回填真实结果，而不是写空泛说明

## Database Migration Policy

数据库迁移是否强制，取决于 `spec/project-architecture/tech-stack.md` 中定义的技术栈。

经验规则：

- 受管迁移工具存在时，例如 Django ORM、Alembic、Aerich，schema 变更必须带迁移脚本
- 如果技术栈明确说明由手工 DDL 管理 schema，ORM migration 文件可以不是强制项
- 如果技术栈没写清楚，这本身就是关键缺口

## Files in This Skill

- `README.md`
  - 面向 GitHub 读者，解释 skill 的定位、独特概念和使用方式
- `SKILL.md`
  - 面向模型执行，定义硬规则、流程和门禁
- `REFERENCE.md`
  - 模板、例子、缺口分类和 migration 格式补充资料

推荐阅读顺序：

1. `README.md`
2. `SKILL.md`
3. `REFERENCE.md`

## Example Usage Intent

- “用 nemesis-coding 帮我把这个模块需求先整理成 spec，再开始实现。”
- “用 nemesis-coding 继续维护这个项目，先补 migration 和测试。”
- “用 nemesis-coding 把旧 docs 和旧 spec-migrations 合并成新的活动 spec 基线。”

## In One Sentence

nemesis-coding 不是让 AI 更快写代码，而是让 AI 在业务与技术锁步的前提下写出可持续维护的代码。
