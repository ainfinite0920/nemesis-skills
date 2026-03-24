---
name: nemesis-coding
description: >-
  Explicitly invoked backend spec-coding workflow that treats business design
   and project architecture as the primary source of truth. It drives coding,
   testing, and append-only spec-migrations from that approved spec baseline.
---

# Nemesis Coding

Spec-first backend workflow for project-level or module-level delivery with
hard alignment gates between business intent, architecture, code, tests, and
spec-migrations.

## Critical Rules (MUST follow)

1. **Explicit invocation only** — MUST use this skill only when the user
   explicitly asks for `nemesis-coding`.
2. **Spec before code** — MUST show a spec skeleton or spec draft and obtain
   approval before implementation begins.
3. **Fixed spec directories** — MUST use `spec/business-design/`,
   `spec/technical-implementation/`, `spec/project-architecture/`, and
   `spec/spec-migrations/`. MUST map or consolidate legacy docs into this fixed
   tree before coding instead of creating parallel sources of truth.
4. **Business over framework** — MUST derive technology choices from
   `spec/project-architecture/tech-stack.md`; MUST NOT hard-code Python or Java
   assumptions before reading the spec.
5. **Tests are mandatory** — MUST create unit tests for every new feature; MUST
   add at least one integration or API test when the change crosses layers.
6. **Migration record is mandatory** — MUST draft a new spec-migration before
   coding, then backfill verification steps and impacted files after coding.
7. **Append-only history** — MUST NOT silently rewrite old spec-migrations;
   corrections MUST be recorded in new migrations.
8. **Pause on critical gaps** — MUST stop coding when critical gaps or spec-code
   drift appear.

## When to Use

- User explicitly invokes `nemesis-coding` for backend project or module work.
- User wants AI to scaffold or repair a spec directory before coding.
- User wants strict traceability from business design to code, tests, and
  spec-migrations.
- User wants long-term maintainable iteration records for future AI changes.

## When NOT to Use

- Frontend-only work or visual design changes; use the default agent or a
   frontend-focused workflow instead.
- Pure infrastructure or deployment tasks without business-domain changes; use
   infrastructure tooling or the default agent instead.
- Quick prototype spikes where spec approval would be unnecessary overhead; use
   the default agent instead.
- Generic backend spec workflows that do not need hard migration and testing
   gates; use a lighter default coding flow instead.

## Input Contract

- MUST expect a `spec/` root.
- MUST require these minimum directories before coding starts:
  - `spec/business-design/`
  - `spec/technical-implementation/`
  - `spec/project-architecture/`
- MUST require `spec/spec-migrations/` before closing the task.
- MUST require `spec/project-architecture/DDD/`,
  `spec/project-architecture/tech-stack.md`, and
  `spec/project-architecture/architecture-overview.md`.
- MAY scaffold missing directories and starter files when the user requests
  fuzzy-requirement or partial-spec work.

## Entry Modes

### Mode 1: Fuzzy Requirement Programming

1. MUST generate a complete but rough spec draft across the fixed directories.
2. MUST present the draft to the user for correction.
3. MUST wait for approval before coding.

**Done when:** Approved spec exists and unresolved critical gaps are zero.

### Mode 2: Detailed Requirement Programming

1. MUST inspect the existing spec tree.
2. MUST scaffold any missing required directories or files.
3. MUST classify gaps as critical or non-critical.
4. MAY fill non-critical gaps with explicit assumptions.
5. MUST pause on critical gaps until the user clarifies them.

**Done when:** Spec is complete enough for tests and migration intent to be
derived without guessing.

## End-to-End Workflow

Use phase markers: `======== PHASE N: [NAME] ========`

### Phase 1: Inspect Spec

1. MUST use discovery tools to locate existing business docs, architecture docs,
   and migration records before declaring the working spec baseline.
2. MUST read the current `spec/` tree when it exists.
3. MUST map legacy project docs into the fixed spec tree when the repo uses
   older layouts such as separate `docs/` and `spec-migrations/` folders.
4. MUST verify the fixed directory contract.
5. MUST read `tech-stack.md` before choosing implementation patterns.
6. SHOULD read existing recent spec-migrations for change context.

**Done when:** Current spec state, stack, and iteration context are understood.

### Phase 2: Repair or Draft Spec

1. MUST create missing required directories.
2. MUST draft or repair business design before technical details.
3. MUST keep DDD material under `spec/project-architecture/DDD/` as a
   directory, not a single oversized file.
4. SHOULD split DDD by topic when that makes boundaries clearer.

**Done when:** The spec tree can drive coding and testing.

### Phase 3: Approval Gate

1. MUST show the spec draft, missing assumptions, and non-critical AI fills.
2. MUST ask for approval before coding.
3. MUST refuse to start implementation without approval.

**Done when:** The user approves the spec baseline.

### Phase 4: Draft Spec-Migration

1. MUST create a new file in `spec/spec-migrations/` named
   `YYYY-MM-DD-short-business-change.md`.
2. MUST draft the migration purpose, scope, intended behavior change, and
   expected verification before coding.
3. SHOULD reference affected business concepts and architecture areas.

**Done when:** The iteration intent is documented before implementation starts.

### Phase 5: Implement

1. MUST map code changes back to approved business design and project
   architecture.
2. MUST choose framework patterns from `tech-stack.md` instead of habit.
3. MUST create stack-specific database migration scripts when the chosen ORM or
   framework requires managed migrations.
4. MUST pause and return to spec revision if coding reveals a major mismatch.

**Done when:** Code reflects approved spec and any stack-required migrations are
present.

### Phase 6: Test

1. MUST add unit tests for the new feature.
2. MUST add at least one integration or API test for cross-layer changes.
3. SHOULD align test case names with business rules from the spec.
4. MUST treat missing tests as incomplete work.

**Done when:** Required tests exist and pass or are blocked for an explicit
environment reason.

### Phase 7: Backfill Migration and Close

1. MUST update the new spec-migration with actual impacted files.
2. MUST run actual test commands or equivalent validation commands when the
   environment allows it.
3. MUST update the verification section with real validation steps and outcomes.
4. SHOULD update related docs when the public contract changed.
5. MUST summarize any assumptions that remain unresolved.

**Done when:** Spec, code, tests, and migration record tell the same story.

## Gap Classification

Critical gaps MUST block coding. Critical gaps include:

- business rules and state transitions
- DDD boundaries, aggregate responsibilities, and entity relationships
- API contracts and input-output semantics
- persistence constraints
- auth and permission rules
- test acceptance criteria
- migration purpose and impact scope
- external dependency side effects

Non-critical gaps MAY be AI-filled, but MUST be shown to the user before coding.

## Drift and Pause Rules

- MUST stop if implementation would change approved business semantics.
- MUST stop if tests cannot be derived from the current spec.
- MUST stop if migration intent and actual code impact diverge.
- SHOULD propose the smallest spec revision needed to resume.
- MAY continue only after user approval of the revised spec.

## Compaction and Recovery

- SHOULD resume by rereading the current `spec/` tree before taking new action.
- SHOULD inspect the latest file in `spec/spec-migrations/` to recover current
   iteration intent.
- MUST restate unresolved assumptions and approval status before resuming code
   changes.
- MAY continue immediately only when the approved spec baseline is still valid.

## Completion Checklist

1. MUST have approved spec directories and required files.
2. MUST have a new append-only spec-migration.
3. MUST have new feature unit tests.
4. MUST have integration or API coverage for cross-layer changes.
5. MUST have stack-required database migration scripts when applicable.
6. MUST report unresolved assumptions and environment blockers.

## Companion Reference

See `REFERENCE.md` for directory templates, migration templates, examples, and
gap triage aids.

## Version History

| Version | Date       | Description |
| ------- | ---------- | ----------- |
| 1.0     | 2026-03-19 | Initial nemesis-coding workflow for strict backend spec-coding with fixed spec directories, approval gates, mandatory tests, and append-only spec-migrations. |