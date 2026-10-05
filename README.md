# Campus Customs — Homework 4

Campus Customs is a Yale-inspired storefront with catalogue browsing, product detail pages, account creation/login, database-backed inventory answers, dynamic chat search cards, customer memory, and a PydanticAI shopping assistant.

## Public-repository safety

This repository intentionally does not include the real `.env`, `campus_customs.db`, or product JPG files. Product media and the database are local course assets. Copy `.env.example` to `.env` and provide your own model key for chat. Never commit secrets.

## Layout

- `frontend/` — React + Vite + TypeScript app
- `backend/main.py` — FastAPI app
- `backend/agent.py` — PydanticAI agent wiring
- `backend/models.py` — Pydantic/PydanticAI types
- `backend/tools.py` — database lookup and audit tools
- `backend/prompts/prompt.md` — agent system prompt
- `output/` — harness, design/usability notes, app-check page, screenshots, and audit trail

## Run the frontend

From `frontend/`:

```bash
npm install
npm run dev
```

Open `http://localhost:5173/`.

## Run the backend

Put the local `campus_customs.db` and `products/` folder next to `backend/` in the Homework 4 directory. From `backend/`:

```bash
pip install -r ../requirements.txt
uvicorn main:app --reload --port 8000
```

The API documentation is available at `http://localhost:8000/docs`.

## Evidence

Open `output/app_check.html` directly in a browser. It links to the three screenshots in `output/app_check_images/` for database-backed stock, dynamic chat product cards, and the category-filter usability improvement.
