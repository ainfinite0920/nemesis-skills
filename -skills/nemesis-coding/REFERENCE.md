# Nemesis Coding Reference

Companion file for `SKILL.md`. Use this file for templates, examples, and
decision aids that would otherwise push the core skill beyond 300 lines.

## Fixed Spec Tree

```text
spec/
  business-design/
    overview.md
    business-rules.md
    workflows.md
  technical-implementation/
    implementation-plan.md
    infrastructure.md
    database.md
    environment.md
  project-architecture/
    architecture-overview.md
    tech-stack.md
    DDD/
      bounded-contexts.md
      aggregates.md
      invariants.md
      application-flows.md
  spec-migrations/
    YYYY-MM-DD-short-business-change.md
```

Rules:

- The four top-level directories are mandatory.
- Directory names are fixed and MUST NOT be renamed casually.
- `DDD/` is mandatory under `project-architecture/`.
- Files inside each directory MAY be split further when that improves clarity.
- If the repo already keeps business docs or migration notes elsewhere, first
  consolidate or map them into this fixed tree before coding so there is only
  one active spec baseline.

## Mode Guide

### Fuzzy Requirement Programming

Use when the user has business intent but not a complete spec.

Suggested flow:

1. Draft the entire fixed spec tree.
2. Keep business language ahead of technical detail.
3. Show the draft and collect corrections.
4. Ask for approval.
5. Draft the spec-migration.
6. Implement code and tests.
7. Backfill the migration with actual impact.

### Detailed Requirement Programming

Use when the user already has partial or complete spec materials.

Suggested flow:

1. Audit the current `spec/` tree against the fixed structure.
2. List missing files and classify their gaps.
3. Fill non-critical gaps with explicit assumptions.
4. Pause on critical gaps.
5. Ask for approval once the spec is code-ready.
6. Draft the spec-migration.
7. Implement code and tests.

## Gap Triage Table

| Area | Default Class | Why |
| ---- | ------------- | --- |
| Status transition rules | Critical | Tests and behavior cannot be trusted without them |
| Aggregate boundaries | Critical | Prevents wrong responsibilities and side effects |
| API request/response meaning | Critical | Interface code would be guesswork |
| Persistence limits and schema rules | Critical | Can break storage and migration safety |
| Auth and permission rules | Critical | Security semantics cannot be guessed |
| Acceptance criteria | Critical | Test targets would be invented |
| Migration purpose and impact scope | Critical | History becomes meaningless without this |
| External dependency side effects | Critical | Integration code may violate real constraints |
| Naming consistency in docs | Non-critical | Can be normalized later if semantics are intact |
| Example payload richness | Non-critical | Can be filled as long as contracts are stable |
| Supplemental diagrams | Non-critical | Useful, but not required to start coding |

## Spec-Migration Template

File name:

```text
spec/spec-migrations/YYYY-MM-DD-short-business-change.md
```

Template:

```markdown
# YYYY-MM-DD Business Change Title

- 目的：说明为什么要做这次业务迭代。
- 变更范围：说明影响的是哪一层或哪几个模块。

## 变更内容
- 列出业务规则、接口、状态流转、依赖变化。

## 受影响文件
- 编码完成后回填真实文件路径。

## 行为前后对比
- 之前：
- 之后：

## 验证
1. 编码前先写预期验证步骤。
2. 编码后回填实际验证结果。

## 备注
- 记录暂不处理项、回滚提示、兼容性说明。
```

## Stack-Specific Migration Rule of Thumb

Create database migration scripts when the stack requires managed schema
migrations.

Examples:

- Django ORM or Alembic-managed SQLAlchemy: migration scripts are mandatory when
  schema changes.
- Spring Boot with manually managed DDL and mapping XML: ORM migration files MAY
  be absent if the stack spec clearly says schema is managed manually.
- If the stack spec is ambiguous, treat migration handling as a critical gap and
  pause.

## Review Prompts for Approval Gates

Before coding:

```text
I have prepared or repaired the spec tree, listed AI-filled non-critical gaps,
and identified any blockers. Please approve the spec baseline before coding.
```

When drift is found:

```text
Implementation uncovered a mismatch between spec and code intent. I am pausing
to revise the spec first. Please approve the revised spec before I continue.
```

## Legacy Layout Mapping

When a repo already has older layouts such as `docs/` plus a top-level
`spec-migrations/` directory, use this order:

1. Discover the existing files first.
2. Decide which ones become the active source for `spec/business-design/` and
  `spec/spec-migrations/`.
3. Consolidate or copy the active content into the fixed spec tree.
4. Continue coding only after the fixed tree becomes the single source of
  truth.

## Failure Modes

1. Missing `tech-stack.md`
   - Treat as critical. Do not choose framework conventions yet.
2. User asks to skip spec and code directly
   - Refuse. Produce the minimum spec skeleton first.
3. Existing migration is wrong
   - Add a new corrective migration. Do not silently edit history.
4. Tests pass but migration intent no longer matches
   - Pause and repair the migration plus spec before closing.
5. Code change crosses layers but only unit tests were added
   - Treat as incomplete. Add integration or API coverage.