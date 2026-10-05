"""Campus Customs API foundation.

This starts as a read-only product and image service. It is intentionally
small so the agent/chat endpoints can be added in Problem 5.
"""

from __future__ import annotations

import json
import hashlib
import hmac
import os
import secrets
import sqlite3
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv

try:
    from .agent import shop_agent
    from .models import ChatRequest, ChatResponse, ShopDependencies
    from .tools import append_audit_event
except ImportError:  # Supports `uvicorn main:app` from the backend folder.
    from agent import shop_agent
    from models import ChatRequest, ChatResponse, ShopDependencies
    from tools import append_audit_event


BACKEND_DIR = Path(__file__).resolve().parent
HW4_DIR = BACKEND_DIR.parent
DATABASE_PATH = HW4_DIR / "campus_customs.db"
PRODUCTS_DIR = HW4_DIR / "products"
load_dotenv(HW4_DIR / ".env")

app = FastAPI(title="Campus Customs API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.mount("/media/products", StaticFiles(directory=PRODUCTS_DIR), name="product-images")


class CreateAccountRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


def password_hash(password: str) -> str:
    """Create a one-way scrypt password hash; the password is never stored."""
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(
        password.encode(), salt=salt, n=2**14, r=8, p=1, dklen=32
    )
    return f"scrypt$16384$8$1${salt.hex()}${digest.hex()}"


def password_matches(password: str, stored_hash: str) -> bool:
    try:
        parts = stored_hash.split("$")
        if parts[0] == "scrypt" and len(parts) == 6:
            _, n, r, p, salt_hex, expected = parts
            actual = hashlib.scrypt(
                password.encode(),
                salt=bytes.fromhex(salt_hex),
                n=int(n),
                r=int(r),
                p=int(p),
                dklen=32,
            ).hex()
            return hmac.compare_digest(actual, expected)
        # Existing seeded accounts use this older format. New registrations
        # always use scrypt above.
        if parts[0] == "pbkdf2_sha256" and len(parts) == 3:
            _, salt, expected = parts
            actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120_000).hex()
            return hmac.compare_digest(actual, expected)
        return False
    except ValueError:
        return False


def connect_database() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def product_from_row(row: sqlite3.Row, inventory: list[dict]) -> dict:
    product = dict(row)
    product["colors"] = json.loads(product["colors"])
    product["search_tags"] = json.loads(product["search_tags"])
    product["inventory"] = inventory
    product["image_url"] = f"/media/{product['image_file_path']}"
    return product


def inventory_for(connection: sqlite3.Connection, product_id: str) -> list[dict]:
    rows = connection.execute(
        "SELECT size, quantity FROM inventory WHERE product_id = ? ORDER BY id",
        (product_id,),
    ).fetchall()
    return [dict(row) for row in rows]


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "campus-customs-api"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Run the Campus Customs shopping agent for one chat message."""
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("PORTKEY_API_KEY"):
        raise HTTPException(status_code=503, detail="The shop assistant is not configured yet")
    customer = None
    history: list[dict] = []
    with connect_database() as connection:
        if request.user_id is not None:
            customer = connection.execute(
                "SELECT id, name, email FROM users WHERE id = ?", (request.user_id,)
            ).fetchone()
            if customer is None:
                raise HTTPException(status_code=401, detail="Logged-in customer not found")
            history = [dict(row) for row in connection.execute(
                "SELECT role, content, created_at FROM chat_messages WHERE user_id = ? ORDER BY id DESC LIMIT 10",
                (request.user_id,),
            ).fetchall()][::-1]
        if request.user_id is not None:
            connection.execute(
                "INSERT INTO chat_messages (user_id, role, content) VALUES (?, 'user', ?)",
                (request.user_id, request.message),
            )
    deps = ShopDependencies(
        database_path=DATABASE_PATH,
        user_id=customer["id"] if customer else None,
        customer_name=customer["name"] if customer else None,
        customer_email=customer["email"] if customer else None,
        chat_history=history,
        page_context=request.page_context,
    )
    try:
        result = await shop_agent.run(
            request.message,
            deps=deps,
        )
        if request.user_id is not None:
            with connect_database() as connection:
                connection.execute(
                    "INSERT INTO chat_messages (user_id, role, content, products_json) VALUES (?, 'assistant', ?, ?)",
                    (request.user_id, result.output.reply, json.dumps([product.model_dump() for product in result.output.products])),
                )
        append_audit_event("agent_loop", {"user_id": request.user_id or "guest", "message_length": len(request.message)}, {"products": len(result.output.products)}, "completed")
        return result.output
    except Exception as error:
        append_audit_event("agent_loop", {"user_id": request.user_id or "guest", "message_length": len(request.message)}, {"error_type": type(error).__name__}, "error")
        raise HTTPException(status_code=502, detail="The shop assistant is temporarily unavailable") from error


@app.get("/api/chat/history/{user_id}")
def chat_history(user_id: int) -> list[dict]:
    with connect_database() as connection:
        user = connection.execute("SELECT id FROM users WHERE id = ?", (user_id,)).fetchone()
        if user is None:
            raise HTTPException(status_code=404, detail="Customer not found")
        rows = connection.execute(
            "SELECT role, content, created_at FROM chat_messages WHERE user_id = ? ORDER BY id",
            (user_id,),
        ).fetchall()
        return [dict(row) for row in rows]


@app.post("/api/auth/register", status_code=201)
def register_account(request: CreateAccountRequest) -> dict:
    if len(request.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    if len(request.password) > 256:
        raise HTTPException(status_code=400, detail="Password is too long")
    email = str(request.email).lower()
    with connect_database() as connection:
        existing = connection.execute("SELECT id FROM users WHERE lower(email) = ?", (email,)).fetchone()
        if existing:
            raise HTTPException(status_code=409, detail="An account with this email already exists")
        full_name = f"{request.first_name.strip()} {request.last_name.strip()}".strip()
        cursor = connection.execute(
            "INSERT INTO users (name, email, password_hash, first_name, last_name) VALUES (?, ?, ?, ?, ?)",
            (full_name, email, password_hash(request.password), request.first_name.strip(), request.last_name.strip()),
        )
        return {"message": "Account created", "user": {"id": cursor.lastrowid, "name": full_name, "email": email}}


@app.post("/api/auth/login")
def login(request: LoginRequest) -> dict:
    email = str(request.email).lower()
    with connect_database() as connection:
        user = connection.execute("SELECT id, name, email, password_hash, first_name, last_name FROM users WHERE lower(email) = ?", (email,)).fetchone()
        if user is None or not password_matches(request.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        if user["password_hash"].startswith("pbkdf2_sha256$"):
            connection.execute(
                "UPDATE users SET password_hash = ? WHERE id = ?",
                (password_hash(request.password), user["id"]),
            )
        return {"message": "Login successful", "user": {"id": user["id"], "name": user["name"], "email": user["email"], "first_name": user["first_name"], "last_name": user["last_name"]}}


@app.get("/api/products")
def list_products(
    search: str | None = Query(default=None, description="Search product names, descriptions, and tags"),
    limit: int = Query(default=100, ge=1, le=200),
) -> list[dict]:
    query = "SELECT * FROM catalogue"
    parameters: list[object] = []
    if search:
        query += " WHERE name LIKE ? OR description LIKE ? OR search_tags LIKE ?"
        term = f"%{search}%"
        parameters.extend([term, term, term])
    query += " ORDER BY name LIMIT ?"
    parameters.append(limit)

    with connect_database() as connection:
        rows = connection.execute(query, parameters).fetchall()
        return [product_from_row(row, inventory_for(connection, row["product_id"])) for row in rows]


@app.get("/api/products/{product_id}")
def get_product(product_id: str) -> dict:
    with connect_database() as connection:
        row = connection.execute(
            "SELECT * FROM catalogue WHERE product_id = ?",
            (product_id,),
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Product not found")
        return product_from_row(row, inventory_for(connection, product_id))
