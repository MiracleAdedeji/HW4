from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
import sqlite3

try:
    from .models import CatalogueSearchResult, ProductLookup, ShopDependencies, StockLine, StockResult
except ImportError:  # Supports direct imports when Uvicorn runs from backend/.
    from models import CatalogueSearchResult, ProductLookup, ShopDependencies, StockLine, StockResult


SEARCH_STOP_WORDS = {
    "a", "an", "and", "are", "do", "does", "for", "have", "i", "in", "is",
    "me", "of", "show", "the", "they", "what", "which", "with", "you", "your", "yall", "y'all", "v", "vs",
}

AUDIT_PATH = Path(__file__).resolve().parent.parent / "output" / "audit_trail.json"


def append_audit_event(tool_name: str, args: dict, result: dict, stop_reason: str) -> None:
    """Append a short, privacy-conscious event without deleting prior events."""
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        events = json.loads(AUDIT_PATH.read_text(encoding="utf-8")) if AUDIT_PATH.exists() else []
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError("Audit trail cannot be read safely; refusing to overwrite it") from error
    if not isinstance(events, list):
        raise RuntimeError("Audit trail must contain a JSON list; refusing to overwrite it")
    events.append({
        "time": datetime.now(timezone.utc).isoformat(),
        "tool_name": tool_name,
        "args": {key: str(value)[:120] for key, value in args.items()},
        "result": {key: str(value)[:240] for key, value in result.items()},
        "stop_reason": stop_reason,
    })
    AUDIT_PATH.write_text(json.dumps(events, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _product(row: sqlite3.Row, connection: sqlite3.Connection) -> ProductLookup:
    inventory = connection.execute(
        "SELECT size, quantity FROM inventory WHERE product_id = ? ORDER BY id",
        (row["product_id"],),
    ).fetchall()
    return ProductLookup(
        product_id=row["product_id"],
        name=row["name"],
        garment_type=row["garment_type"],
        description=row["description"],
        price=row["price"],
        colors=json.loads(row["colors"]),
        image_file_path=row["image_file_path"],
        inventory=[StockLine(size=item["size"], quantity=item["quantity"]) for item in inventory],
    )


def search_catalogue(deps: ShopDependencies, query: str, limit: int = 8) -> CatalogueSearchResult:
    """Find products by name, description, garment type, or search tags."""
    words = []
    for raw_word in query.lower().split():
        word = raw_word.strip("?!.,'")
        if not word or word in SEARCH_STOP_WORDS:
            continue
        words.append(word[:-3] + "ie" if word.endswith("ies") else word)
    if not words:
        result = CatalogueSearchResult()
        append_audit_event("find_products", {"query": "[empty]", "limit": limit}, {"matches": 0}, "completed")
        return result
    clauses = []
    values: list[str | int] = []
    for word in words:
        term = f"%{word}%"
        clauses.append("(name LIKE ? OR garment_type LIKE ? OR description LIKE ? OR search_tags LIKE ?)")
        values.extend([term, term, term, term])
    values.append(limit)
    with sqlite3.connect(deps.database_path) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            f"SELECT * FROM catalogue WHERE ({' OR '.join(clauses)}) ORDER BY name LIMIT ?",
            values,
        ).fetchall()
        result = CatalogueSearchResult(products=[_product(row, connection) for row in rows])
        append_audit_event("find_products", {"query": query, "limit": limit}, {"matches": len(result.products)}, "completed")
        return result


def get_product(deps: ShopDependencies, product_id: str) -> ProductLookup | None:
    """Get one product and its size-level inventory by product ID."""
    with sqlite3.connect(deps.database_path) as connection:
        connection.row_factory = sqlite3.Row
        row = connection.execute("SELECT * FROM catalogue WHERE product_id = ?", (product_id,)).fetchone()
        result = _product(row, connection) if row else None
        append_audit_event("product_details", {"product_id": product_id}, {"found": bool(result)}, "completed")
        return result


def get_stock(deps: ShopDependencies, product_id: str) -> StockResult:
    """Return the real inventory quantity for every size of one product."""
    with sqlite3.connect(deps.database_path) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            "SELECT size, quantity FROM inventory WHERE product_id = ? ORDER BY id",
            (product_id,),
        ).fetchall()
        result = StockResult(
            product_id=product_id,
            stock=[StockLine(size=row["size"], quantity=row["quantity"]) for row in rows],
        )
        append_audit_event("check_stock", {"product_id": product_id}, {"sizes_returned": len(result.stock)}, "completed")
        return result
