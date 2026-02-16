# Lab 3 — Plan (Beginner-First, OBER-Aligned)

## Context

Lab 3 builds on Lab 2, where students already:

- Ran and debugged a FastAPI service
- Used GitHub issues/PRs/reviews
- Used Docker Compose
- Deployed to a Linux VM

From this lab onward, we keep one product across labs: an outcome-based educational recommender inspired by OBER.

We start from a seeded backend:

- Database already contains `items`, `outcomes`, `learners`, `interaction_logs` (anonymized)
- Endpoints for `items`, `outcomes`, `learners` are already implemented
- `/docs` is already available via FastAPI Swagger UI

---

## Design principles for this cohort

1. Start with observation, not coding.
2. Teach REST as a minimal practical contract, not theory-heavy architecture.
3. Reuse existing endpoint patterns for first feature work.
4. Keep one business-logic task (mastery) as the main challenge.
5. Treat security as both app-level (auth/permissions) and server-level (hardening).

---

## REST scope (minimum only)

Students must understand and apply:

- Noun-based resource paths (`/interactions`, `/alignments`)
- Core methods (`GET`, `POST`, `PUT`)
- Core statuses (`200`, `201`, `400/422`, `404`, `401`, `403`)
- Query filters + pagination basics
- Request/response schemas via Pydantic

We intentionally skip advanced REST topics (HATEOAS, versioning strategy, caching semantics).

---

## Story

> "The data team already loaded real anonymized learning data into our DB.
> Your job is to extend the API safely and correctly:
> expose interaction logs, add item-outcome mappings, compute mastery,
> secure the service, and deploy it on a hardened VM."

---

## Required tasks

### Task 1: Explore existing API via Swagger (no coding yet)

Students:

- Run the project and open `/docs`
- Try existing `learners` and `outcomes` endpoints
- Record method, path, status, and response shape examples

Goal: understand API contracts before implementation work.

---

### Task 2: Implement interaction log endpoints (by example)

Students implement:

- `GET /interactions` (filters + pagination)
- `POST /interactions` (validated insert)

Goal: first independent endpoint implementation by copying established project patterns.

---

### Task 3: Add alignments table + endpoints

Students:

- Create alignment mapping table between `items` and `outcomes`
- Implement endpoints to read, add, and edit alignments

Schema simplification (for this cohort):

- Keep alignments as a simple mapping only (`item_id` <-> `outcome_id`)
- Do not introduce relation types in Lab 3

Suggested endpoints:

- `GET /alignments`
- `POST /alignments`
- `PUT /alignments/{id}`

Goal: build the core OBER connection layer used by later labs.

---

### Task 4: Implement and test mastery endpoint

Students:

- Implement mastery calculation endpoint(s)
- Add robust tests for normal and edge cases

Suggested endpoints:

- `GET /mastery/{learner_id}`
- `GET /mastery/{learner_id}/total`

Goal: implement meaningful product logic and prove correctness with tests.

---

### Task 5: Security task (auth/permissions + VM hardening)

This is one combined security task.

App security:

- Add API-key authentication for write operations
- Add simple permission checks (read vs write/admin behavior)
- Return proper auth statuses (`401`, `403`)

Server security:

- Create non-root SSH user for operations
- Configure firewall (`ufw`)
- Configure fail2ban
- Disable root password login
- Create dedicated `checkbot` SSH user (restricted, no sudo)

Goal: connect API security and infrastructure security in one coherent task.

Scope note:

- If this task is too heavy, server hardening can be moved to Lab 4 while keeping API-key auth in Lab 3.

---

### Task 6: Deploy to hardened VM

Students deploy the updated service to their VM and verify:

- Public read endpoints work
- Mastery endpoint works
- Security configuration remains active after deployment

---

## Optional tasks

- Add `DELETE /alignments/{id}`
- Add OpenAPI examples for all new payloads
- Add DB migration tooling (Alembic)
- Add endpoint-level audit logging for write actions

---

## Open questions

1. Hardening depth:
Should we require `PasswordAuthentication no` for everyone, or allow key-only root-disabled minimum?

2. Checkbot restrictions:
Command-restricted SSH key now, or in a later lab?

3. CI placement:
CI checks are a good candidate for Lab 4 if Lab 3 scope gets tight.

4. Scope pressure:
If needed, split Task 5:
- Lab 3: API-key auth + minimal permissions
- Lab 4: full hardening checklist + CI
