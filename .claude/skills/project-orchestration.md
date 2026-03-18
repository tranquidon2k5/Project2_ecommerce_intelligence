---
name: Project Orchestration
description: How to delegate tasks to subagents and track project progress
---

# Project Orchestration Skill

## Architecture: Agents → Skills → Tasks

```
CLAUDE.md (project context — always loaded)
    │
    ├── .claude/agents/    (8 role-based agents — WHO does the work)
    │   ├── infrastructure-setup.md
    │   ├── database-models.md
    │   ├── backend-api.md
    │   ├── crawler.md
    │   ├── frontend.md
    │   ├── ml-ai.md
    │   ├── devops-deploy.md
    │   └── testing.md
    │
    ├── .claude/skills/    (10 procedure-based skills — HOW to do the work)
    │   ├── fastapi-endpoint.md
    │   ├── sqlalchemy-model.md
    │   ├── scrapy-spider.md
    │   ├── react-page.md
    │   ├── react-chart.md
    │   ├── ml-model.md
    │   ├── docker-service.md
    │   ├── pydantic-schema.md
    │   ├── redis-caching.md
    │   └── testing-backend.md
    │
    └── PROGRESS.md        (progress tracker — WHAT has been done)
```

## How to Delegate Work

### Method 1: Direct Agent Invocation (Claude Code)

Use the `/agent` command in Claude Code to invoke a specific subagent:

```
/agent infrastructure-setup
Setup Docker Compose với 5 services theo planning/02_ARCHITECTURE.md

/agent database-models
Tạo tất cả SQLAlchemy models theo planning/03_DATABASE_SCHEMA.md

/agent backend-api
Implement Product API endpoints theo planning/04_API_DESIGN.md
```

### Method 2: Prompt with Agent Context

Reference the agent file directly in your prompt:

```
Đọc file .claude/agents/backend-api.md và thực hiện Task 1 (Product Service & API).
Tham chiếu planning/04_API_DESIGN.md cho chi tiết endpoints.
```

### Method 3: Follow the Sprint Plan Sequentially

Use prompts from `planning/07_CLAUDE_CODE_PROMPTS.md` — each prompt is pre-written and maps to a specific sprint task. Copy-paste one prompt at a time.

## Task-to-Agent Mapping

### Sprint 1: Foundation (Day 1-5)
| Task | Agent | Skills Used |
|------|-------|-------------|
| Folder structure + Docker + configs | `infrastructure-setup` | `docker-service` |
| SQLAlchemy models + migrations | `database-models` | `sqlalchemy-model` |
| Pydantic schemas + seed data | `database-models` | `pydantic-schema` |
| Core API endpoints (products) | `backend-api` | `fastapi-endpoint`, `redis-caching` |
| Scrapy setup + Tiki spider | `crawler` | `scrapy-spider` |

### Sprint 2: Frontend + Data (Day 6-10)
| Task | Agent | Skills Used |
|------|-------|-------------|
| React setup + layout | `frontend` | `react-page` |
| Dashboard + Search pages | `frontend` | `react-page`, `react-chart` |
| Product Detail page | `frontend` | `react-page`, `react-chart` |
| Shopee spider | `crawler` | `scrapy-spider` |
| Analytics + Alerts API | `backend-api` | `fastapi-endpoint` |
| Compare + Trending pages | `frontend` | `react-page`, `react-chart` |

### Sprint 3: AI Features (Day 11-15)
| Task | Agent | Skills Used |
|------|-------|-------------|
| Price prediction (Prophet) | `ml-ai` | `ml-model` |
| Anomaly detection (IsolationForest) | `ml-ai` | `ml-model` |
| Review analysis + Buy signal | `ml-ai` | `ml-model` |
| AI Insights frontend page | `frontend` | `react-page`, `react-chart` |
| APScheduler integration | `ml-ai` | — |

### Sprint 4: Polish + Deploy (Day 16-20)
| Task | Agent | Skills Used |
|------|-------|-------------|
| Performance + data scale | `devops-deploy` | `redis-caching` |
| Monitoring + logging | `devops-deploy` | `fastapi-endpoint` |
| UI polish + dark mode | `frontend` | `react-page` |
| Docker prod + deploy | `devops-deploy` | `docker-service` |
| README + CI/CD | `devops-deploy` | — |
| Write tests | `testing` | `testing-backend` |

## Recommended Workflow

```
1. Mở PROGRESS.md → Tìm task tiếp theo chưa hoàn thành
2. Xác định agent phụ trách (cột Agent)
3. Mở planning doc tương ứng để nắm yêu cầu chi tiết
4. Copy prompt từ 07_CLAUDE_CODE_PROMPTS.md (hoặc viết custom prompt)
5. Chạy prompt (invoke agent nếu dùng Claude Code)
6. Verify kết quả (test, check UI, check API docs)
7. Cập nhật PROGRESS.md: [ ] → [x]
8. Git commit + push
9. Lặp lại
```

## Rules

1. **Mỗi lần chỉ chạy 1 agent** — Đừng gộp nhiều tasks
2. **Verify trước khi tiếp** — Chạy thử, test endpoint, check UI
3. **Fix lỗi ngay** — Paste error log vào Claude Code để fix
4. **Commit thường xuyên** — Sau mỗi task thành công
5. **Theo thứ tự sprint** — Sprint 1 phải xong trước Sprint 2
6. **Dependencies matter** — infrastructure-setup → database-models → backend-api → frontend
