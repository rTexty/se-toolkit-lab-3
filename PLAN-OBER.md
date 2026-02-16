# Lab 3 — OBER Plan (Beginner-First)

## Context

Lab 3 builds on Lab 2, where students already:

- Ran and fixed a FastAPI service
- Used issues, branches, PRs, and reviews
- Used Docker Compose
- Deployed to a Linux VM

From Lab 3 onward, labs build one product: an outcome-based educational recommender inspired by OBER ([arXiv:2509.18186](https://arxiv.org/abs/2509.18186)).

The platform centers on:

- Learning content (`items`)
- Learning goals (`outcomes`)
- Learners (`learners`)
- Interactions (`interaction_logs`)
- Item-outcome mapping (`alignments`)
- Progress estimation (`mastery`)

---

## Starter repo assumptions

Students get a repo (derived from Lab 2) where:

- PostgreSQL is already configured
- DB is pre-seeded with anonymized real-world style data
- `items`, `outcomes`, `learners` read endpoints already work
- `/docs` (Swagger UI) already works
- A small example test file exists

This lets us focus on API extension, business logic, testing, and security.

---

## Beginner guardrails (REST-lite)

Many students see REST for the first time here. We keep scope intentionally small:

1. Resource paths use nouns (`/interactions`, `/alignments`).
2. Core methods only (`GET`, `POST`, `PUT`).
3. Core statuses only (`200`, `201`, `404`, `422`, `401`, `403`).
4. Query params for filtering/pagination.
5. Pydantic schemas as API contract.

No advanced REST topics in this lab (HATEOAS, versioning strategies, caching semantics).

---

## Story

> "Data is already loaded: items, outcomes, learners, and interaction logs.
> Your job is to extend the API safely:
> expose interactions, add alignments, compute mastery,
> secure the service, and deploy it to a hardened VM."

---

## Required tasks

### Task 1: Explore API docs and existing endpoints (no coding)

Students:

- Open `/docs`
- Explore `GET /learners`, `GET /learners/{id}`, `GET /outcomes`, `GET /outcomes/{id}`
- Run sample calls and inspect statuses + response schemas
- Submit short observations (method/path/status/shape)

Goal:

- Understand the API contract before writing code
- Learn by reading implemented "standard" endpoints first

Autochecker evidence:

- Process checks (`issue_exists`, `pr_merged_exists`) for task completion workflow

---

### Task 2: Implement interaction endpoints by example

Students implement:

- `GET /interactions` with optional filters + pagination
- `POST /interactions` with validation

Suggested request model:

- `learner_id`, `item_id`, `progress`, `session_number`

Core rules:

- `progress` in `[0.0, 1.0]`
- unknown `learner_id` / `item_id` rejected
- `POST` returns `201`

Autochecker evidence:

- API behavior tests in repo (`clone_and_run`)
- Optional deployment `http_check` for `GET /interactions`
- Process checks (issue/PR)

---

### Task 3: Add alignments table + endpoints

Students:

- Create table mapping `items` to `outcomes`
- Implement endpoints to read, add, and edit mappings

Suggested endpoints:

- `GET /alignments`
- `POST /alignments`
- `PUT /alignments/{id}`

Suggested fields:

- `item_id`
- `outcome_id`
- `relation_type` (`promotes` or `verifies`)

Core rules:

- relation type validation
- FK validation for item/outcome
- duplicate mapping protection

Autochecker evidence:

- Table/model presence check (`regex_in_file`)
- Endpoint behavior via tests (`clone_and_run`)
- Process checks (issue/PR)

---

### Task 4: Implement mastery endpoint and test it properly

Students implement:

- `GET /mastery/{learner_id}`
- (optional companion) `GET /mastery/{learner_id}/total`

Simplified mastery logic:

1. Use alignments linked to outcomes.
2. Use learner interactions to estimate progress per outcome.
3. Return deterministic scores with clear response schema.

Testing requirements:

- happy path
- no-data path
- invalid learner
- threshold/aggregation behavior

Autochecker evidence:

- `clone_and_run`: all tests pass
- endpoint-level assertions in tests for schema and score range

---

### Task 5: Security task (auth/permissions + server hardening)

This is one combined task with app and infra security.

App security:

- Add simple authentication for write endpoints
- Add permission checks (at least read vs write roles)
- Correct status behavior:
  - missing/invalid auth -> `401`
  - insufficient permissions -> `403`

Server hardening:

- Create non-root SSH user for operations
- Configure firewall (`ufw`)
- Configure fail2ban for SSH
- Disable root password login
- Create dedicated `checkbot` user for verification access
- `checkbot` must be restricted (no sudo)

Autochecker evidence:

- App auth/permission checks via repository tests (`clone_and_run`)
- VM hardening checks via `checkbot` SSH verification script

---

### Task 6: Deploy to hardened VM

Students deploy updated backend to VM and validate:

- service is reachable
- read endpoints work
- mastery endpoint works
- security settings remain active

Autochecker evidence:

- deployment `http_check` for public read/mastery endpoints
- hardening verification via `checkbot`

---

## Why this sequence works

1. Starts with observation and confidence (`/docs`) for first-time REST learners.
2. First coding task is pattern-copying, not architecture invention.
3. Business logic challenge (mastery) comes after data model is in place.
4. Security is treated end-to-end: app auth + VM hardening together.
5. Deployment closes the loop with machine-verifiable outcomes.

---

## Outcomes that are log/checker verifiable

For reliable grading and dashboard tracking, each task should emit machine-checkable evidence:

1. Process evidence: issues, PRs, approvals.
2. Code evidence: models/endpoints/tests in repo.
3. Runtime evidence: passing tests and deployed HTTP responses.
4. Security evidence: remote checks through restricted `checkbot`.

This keeps grading tied to reproducible signals, not manual screenshots.

---

## Open questions

1. Auth format for beginners:
use simple API keys this lab, defer JWT to a later lab?

2. Permission granularity:
single write role vs separate instructor/admin role?

3. Alignment semantics naming:
standardize on `promotes/verifies` now, or keep `assesses/promotes`?

4. Required test count:
fixed minimum number, or coverage by behavior checklist?

5. Checkbot policy:
command-restricted SSH key in this lab vs next lab?
