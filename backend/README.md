# Campus Customs backend

## Run locally

From the `backend` directory:

```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Useful endpoints:

- `GET http://localhost:8000/api/health`
- `GET http://localhost:8000/api/products`
- `GET http://localhost:8000/api/products?search=hoodie`
- `GET http://localhost:8000/api/products/{product_id}`
- Product images: `http://localhost:8000/media/products/{filename}`
- `POST http://localhost:8000/api/auth/register`
- `POST http://localhost:8000/api/auth/login`

Registration expects `first_name`, `last_name`, `email`, and `password`. Login expects `email` and `password`.

Passwords for new accounts are stored only as salted, one-way scrypt hashes. The original passwords are never written to the database or returned by the API. Existing seeded PBKDF2-SHA256 accounts remain readable for compatibility, while new registrations use scrypt.

The PydanticAI agent is split into `prompts/prompt.md` for the growing system prompt, `agent.py` for agent wiring, `tools.py` for database tools, and `models.py` for Pydantic/PydanticAI types. It uses `gpt-5.6-luna` by default, configurable with `CAMPUS_CUSTOMS_MODEL`. Set `OPENAI_API_KEY` for direct OpenAI access. The repository's existing `PORTKEY_API_KEY` is also supported through Portkey's OpenAI-compatible gateway. Keep keys in environment variables or `.env`, never in source code.

The `/api/chat` endpoint is ready for the frontend chat widget. Agent and chat behavior can grow here in Problem 5.
