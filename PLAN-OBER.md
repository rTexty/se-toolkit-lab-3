# Lab 3 — OBER Plan

## Context

Lab 3 builds on Lab 2, where students:

- Ran a FastAPI web server locally
- Fixed a bug and submitted a PR
- Ran the server using Docker Compose (with Caddy reverse proxy)
- Deployed to a Linux VM

Starting from Lab 3, all labs build a single product: an **educational recommender platform** inspired by the [OBER paper](https://arxiv.org/abs/2509.18186) (Outcome-Based Educational Recommender). The platform manages learning content, tracks learner progress against defined outcomes, and eventually recommends what to learn next.

The codebase carries forward from Lab 2 through Lab 9. Each lab adds a meaningful capability.

---

## Story

> Your senior engineer says:
>
> "We're building an e-learning platform that recommends content to students based on their progress toward learning outcomes.
>
> The data team has loaded up a database with anonymized data from a real educational app: items (content), outcomes (learning goals), learners, and their interaction logs.
>
> We already have read endpoints for items, outcomes, and learners. Your job is to extend the API, add the missing pieces, write proper tests, and make the server production-ready."

---

## What students receive (starter repo)

The starter codebase is a fork of Lab 2, upgraded with:

- **PostgreSQL** added to `docker-compose.yml` (replacing JSON file storage)
- **SQLAlchemy** models and a session setup
- **Pre-seeded database** with anonymized data from a real educational app:

| Table | ~Rows | Key columns |
|-------|-------|-------------|
| `items` | 100 | `id`, `title`, `type`, `description` |
| `outcomes` | 30 | `id`, `title`, `parent_id` (tree hierarchy) |
| `learners` | 100 | `id`, `created_at` |
| `interaction_logs` | 5,000 | `id`, `learner_id`, `item_id`, `progress` (0.0–1.0), `started_at`, `session_number` |

- **Pre-existing endpoints** (already implemented, serve as patterns to follow):
  - `GET /items`, `GET /items/{id}`
  - `GET /outcomes`, `GET /outcomes/{id}` (includes `parent_id` for tree structure)
  - `GET /learners`, `GET /learners/{id}`
  - `GET /docs` (Swagger UI)
  - `GET /status`

- **One example test file** (`test_items.py`) with 2 tests, demonstrating the TestClient + DB fixture pattern

Note: the `interaction_logs` table has data but **no endpoints** — students implement those.

---

## Proposed structure

### Task 0: Explore the API (Swagger)

**Students do:**

- Run `docker compose up`, open `/docs` in the browser
- Try each existing endpoint: `GET /items`, `GET /outcomes`, `GET /learners/{id}`
- Look at the auto-generated request/response schemas
- Read the existing code: models → service → router pattern
- Create a GitHub issue: `[Task 0] Explore the API`
- Paste 3 Swagger responses (screenshots or JSON) in the issue body, close it

**Key concepts:** OpenAPI, Swagger UI, interactive API docs, API contract.

**Why first:** Immediate visual payoff. Students see something tangible before writing code. They also learn the codebase patterns they'll replicate.

**Autochecker:**

- `repo_exists`, `repo_is_fork`, `repo_has_issues`
- `issue_exists`: title matches `\[Task 0\]`, state closed

---

### Task 1: Implement interaction log endpoints

The `interaction_logs` table exists and has data, but there are no API endpoints for it. Students look at the existing items/outcomes endpoints as examples and replicate the pattern.

**Students implement:**

```
GET  /interactions?learner_id={id}&item_id={id}&limit=20&offset=0
POST /interactions
     body: { learner_id, item_id, progress, session_number }
```

**Requirements:**

- Both query filters are optional, combinable
- Validate: `progress` must be in `[0.0, 1.0]` → 422 otherwise
- Validate: `learner_id` and `item_id` must reference existing records → 404 otherwise
- Pagination via `limit` (default 20) and `offset` (default 0)
- `POST` returns 201 with the created object (including generated `id` and `started_at`)

**Key concepts:** REST conventions, query parameters, input validation, foreign key checks, HTTP status codes.

**Autochecker:**

- `http_check`: `POST /interactions` with valid body → 201
- `http_check`: `POST /interactions` with `progress: 1.5` → 422
- `http_check`: `POST /interactions` with nonexistent `learner_id` → 404 or 422
- `http_check`: `GET /interactions?learner_id=L001` → 200, response is a list
- `http_check`: `GET /interactions?learner_id=L001&limit=5` → ≤5 items in response
- `issue_exists` + `pr_merged_exists` for the task

---

### Task 2: Create the alignments table and endpoints

This is the core [OBER](https://arxiv.org/abs/2509.18186) concept. Alignments define which items assess or promote which learning outcomes. The table doesn't exist yet — students create it from scratch (migration script or SQLAlchemy model + `create_all`).

**New table:**

```sql
alignments
    id              SERIAL PRIMARY KEY
    item_id         INTEGER REFERENCES items(id)
    outcome_id      INTEGER REFERENCES outcomes(id)
    relation_type   VARCHAR(20) CHECK (relation_type IN ('assesses', 'promotes'))
    UNIQUE(item_id, outcome_id, relation_type)
```

**New endpoints:**

```
GET    /alignments?outcome_id={id}&item_id={id}&relation_type=assesses
POST   /alignments         → body: { item_id, outcome_id, relation_type }
PATCH  /alignments/{id}    → partial update
DELETE /alignments/{id}    → 204
```

**Requirements:**

- `relation_type` must be `'assesses'` or `'promotes'` → 422 otherwise
- Duplicate `(item_id, outcome_id, relation_type)` → 409 Conflict
- Foreign key validation — referenced item and outcome must exist
- All `GET` filters are optional and combinable
- `POST` returns 201
- `DELETE` returns 204, subsequent `GET` by that id returns 404

**Why this matters:** Students are building the knowledge graph that connects learning content to learning goals. This is what makes the recommender "outcome-based" rather than popularity-based. In later labs, the ML model uses these alignments to weight recommendations.

**Autochecker:**

- `http_check`: `POST /alignments` with valid body → 201
- `http_check`: `POST /alignments` with same body again → 409
- `http_check`: `POST /alignments` with `relation_type: "invalid"` → 422
- `http_check`: `GET /alignments?outcome_id=1` → 200, filtered list
- `http_check`: `DELETE /alignments/{id}` → 204
- `regex_in_file`: model file contains `alignments` table/class definition
- `issue_exists` + `pr_merged_exists`

---

### Task 3: Implement the mastery endpoint

This is the business logic challenge. Mastery answers the question: *"How well does a learner know each outcome?"* It requires joining data across interactions and alignments.

**Students implement:**

```
GET /learners/{id}/mastery?threshold=0.8
```

**Response:**

```json
[
    {
        "outcome_id": 1,
        "outcome_title": "Fard Prayers",
        "mastery_score": 0.72,
        "items_studied": 3,
        "items_total": 5,
        "achieved": false
    }
]
```

**Calculation (simplified from the real [namaz-recommender](https://arxiv.org/abs/2509.18186) codebase):**

1. For each outcome, find all items where `alignment.relation_type = 'assesses'`
2. For each aligned item, find the learner's **best** progress (`MAX(progress)` across all their interactions with that item)
3. `mastery_score` = mean of those best-progress values (0.0 if no interactions)
4. `items_studied` = count of aligned items the learner has interacted with
5. `items_total` = total aligned items for that outcome
6. `achieved` = `mastery_score >= threshold`

**Requirements:**

- Only return outcomes that have at least one alignment (with `relation_type = 'assesses'`)
- `threshold` query param defaults to `0.8`
- Nonexistent learner → 404
- Outcomes where the learner has no interactions → `mastery_score: 0.0`, `achieved: false`

**Why this matters:** Mastery is the metric the entire system optimizes for. The recommender (Lab 8) will try to maximize mastery. The dashboard (Lab 7) will visualize it. The Telegram bot (Lab 6) will show learners their progress.

**Autochecker:**

- `http_check`: `GET /learners/L001/mastery` → 200, response is a list with required keys
- `http_check`: verify all `mastery_score` values are in `[0.0, 1.0]`
- `http_check`: `GET /learners/NONEXISTENT/mastery` → 404
- `http_check`: `GET /learners/L001/mastery?threshold=0.5` → at least as many `achieved: true` as with `0.8`
- Deterministic check: create a known alignment + interaction via POST, then verify mastery reflects it
- `issue_exists` + `pr_merged_exists`

---

### Task 4: Write tests

**Students implement:**

- **Interaction log tests** (at least 4): create, read with filter, validation error (progress out of range), pagination
- **Alignment tests** (at least 4): create, duplicate → 409, delete + verify gone, filter by outcome
- **Mastery tests** (at least 3): happy path with seeded data, empty mastery for learner with no interactions, 404 for nonexistent learner

Students follow the pattern in the provided `test_items.py` — use `TestClient` with a test database fixture.

All tests must pass: `docker compose run api pytest` exits 0.

**Key concepts:** Automated testing, test isolation, fixtures, edge cases, TestClient.

**Autochecker:**

- `clone_and_run`: `uv sync && uv run pytest` → exit code 0
- File glob: test files exist matching `test_*.py` with `def test_` functions (at least 11)
- `issue_exists` + `pr_merged_exists`

---

### Task 5: Harden the server and set up checkbot access

The VM from Lab 2 is a fresh Ubuntu with root SSH access. Students make it production-ready.

**5a. Create a non-root user:**

- `adduser <username>` with sudo privileges
- Set up SSH key authentication for this user
- Verify: `ssh <username>@<vm_ip>` works without a password

**5b. Firewall (ufw):**

- `ufw allow 22/tcp` (SSH)
- `ufw allow 80/tcp` (HTTP — Caddy)
- `ufw allow 443/tcp` (HTTPS — for later labs)
- `ufw enable`
- Everything else is blocked

**5c. fail2ban:**

- Install and enable fail2ban
- Default SSH jail active (bans IPs after failed login attempts)

**5d. Disable root password login:**

- `/etc/ssh/sshd_config`: `PermitRootLogin prohibit-password` (key-only)
- `PasswordAuthentication no`
- Restart sshd

**5e. Create `checkbot` user:**

- Dedicated user, no sudo access
- Add the course-provided public SSH key to `checkbot`'s `authorized_keys`
- The autochecker uses this account to verify the deployment and hardening

**Key concepts:** Principle of least privilege, SSH key auth, firewall, brute-force protection, service accounts.

**Autochecker (via SSH as `checkbot`):**

- SSH connects as `checkbot@{server_ip}` → success
- `sudo -n whoami` → fails (checkbot has no sudo)
- `systemctl is-active fail2ban` → active
- Grep `/etc/ssh/sshd_config` → `PermitRootLogin prohibit-password` and `PasswordAuthentication no`

---

### Task 6: Deploy

**Students do:**

- Push their code to the VM (git clone/pull, or rsync)
- `docker compose up -d` on the VM
- Seed script runs on startup, DB is populated
- Verify: all endpoints work when queried from outside the VM

**Autochecker:**

- `http_check` via `{server_ip}`: `GET /docs` → 200
- `http_check`: `GET /items` → 200 with items in response
- `http_check`: `POST /interactions` with valid body → 201
- `http_check`: `GET /learners/L001/mastery` → 200 with valid structure
- `http_check`: `GET /alignments` → 200

---

## What this teaches

| Skill | How it shows up |
|-------|----------------|
| **Swagger / API docs** | Primary exploration tool in Task 0 |
| **RESTful API design** | Status codes, validation, filters, pagination |
| **Database** | Read existing schema, create a new table, write joins |
| **Business logic** | Mastery calculation — aggregation across 3 tables |
| **Testing** | TestClient, fixtures, edge cases, CI-like `pytest` runs |
| **Linux ops** | Users, firewall, fail2ban, SSH hardening |
| **Deployment** | Docker Compose on a real VM |
| **Git workflow** | Issue → branch → PR → review → merge per task |

---

## How this connects to future labs

The alignment table + mastery endpoint are the intellectual core of the OBER system. Everything in Labs 4–9 builds on these three concepts: **items**, **outcomes**, and the **mastery score** that connects them.

| Lab | What it adds to the platform |
|-----|------------------------------|
| 4 | AI integration — LLM auto-suggests outcome-item alignments |
| 5 | Telegram bot — learners check their mastery, log interactions |
| 6 | Data analytics + web dashboard — visualize mastery across all learners |
| 7 | ML recommender — train a model that optimizes for mastery |
| 8 | Flutter app — mobile learning companion |
| 9 | Hackathon — ship a real feature |

---

## Open questions

### 1. Starter code preparation

The current Lab 2 codebase uses JSON file storage. We need to prepare the upgraded starter:

- Add PostgreSQL + SQLAlchemy setup
- Create models for items, outcomes, learners, interaction_logs
- Seed script with anonymized namaz-recommender data
- One example test file showing the DB fixture pattern
- Remove the old JSON-reading service layer

This is significant work. Should it be done as a template repo, or should Lab 2 end with a DB so Lab 3 starts cleaner?

### 2. Data anonymization

The seed data comes from the real namaz-recommender (~85k learners, ~250 items). We need to:

- Subsample to ~100 learners, ~100 items, ~5k interactions
- Replace all IDs with opaque identifiers (L001, I001, O001)
- Strip multilingual titles down to English only
- Ensure the outcome hierarchy and interaction patterns are preserved

### 3. Alignment seed data

Should the alignments table start empty (students populate it via their new endpoints) or pre-seeded with some mappings? Starting empty means the mastery endpoint returns all zeros until they create alignments — which might actually be a good learning moment.

### 4. Two difficulty levels

Some students need step-by-step guidance, others want just the acceptance criteria. Consider collapsible `<details>` blocks for hints/steps.

### 5. Task sizing

6 tasks is ambitious. If it doesn't fit in one lab session:

- Tasks 0–3 (API work) are the core — these must be required
- Task 4 (tests) could be partially required (e.g., at least 6 tests) with the full 11 as a stretch
- Tasks 5–6 (hardening + deploy) could be a take-home checkpoint before Lab 4
