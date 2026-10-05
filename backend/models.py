from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from pydantic import BaseModel, Field, field_validator


@dataclass
class ShopDependencies:
    database_path: Path
    user_id: int | None = None
    customer_name: str | None = None
    customer_email: str | None = None
    chat_history: list[dict] = field(default_factory=list)
    page_context: dict | None = None


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    user_id: int | None = None
    page_context: dict | None = None

    @field_validator("message")
    @classmethod
    def message_must_contain_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Message must contain text")
        return value


class ChatHistoryMessage(BaseModel):
    role: str
    content: str
    created_at: str


class ProductCard(BaseModel):
    """The safe, customer-facing product data a chat reply may display."""

    product_id: str
    name: str
    garment_type: str
    price: float
    description: str
    colors: list[str] = Field(default_factory=list)
    image_file_path: str | None = None
    inventory: list["StockLine"] = Field(default_factory=list)


class StockLine(BaseModel):
    size: str
    quantity: int


class CatalogueSearchResult(BaseModel):
    products: list[ProductLookup] = Field(default_factory=list)


class StockResult(BaseModel):
    product_id: str
    stock: list[StockLine] = Field(default_factory=list)


class ChatResponse(BaseModel):
    reply: str
    products: list[ProductCard] = Field(default_factory=list)


class ProductLookup(BaseModel):
    product_id: str
    name: str
    garment_type: str
    description: str
    price: float
    colors: list[str]
    image_file_path: str
    inventory: list[StockLine]
