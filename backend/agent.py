from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

try:
    from .models import ChatResponse, CatalogueSearchResult, ProductLookup, ShopDependencies, StockResult
    from .tools import get_product, get_stock, search_catalogue
except ImportError:  # Supports direct imports when Uvicorn runs from backend/.
    from models import ChatResponse, CatalogueSearchResult, ProductLookup, ShopDependencies, StockResult
    from tools import get_product, get_stock, search_catalogue


load_dotenv(Path(__file__).resolve().parents[2] / ".env")
MODEL_NAME = os.getenv("CAMPUS_CUSTOMS_MODEL", "gpt-5.6-luna")
PROMPT_PATH = Path(__file__).resolve().parent / "prompts" / "prompt.md"
SYSTEM_PROMPT = PROMPT_PATH.read_text(encoding="utf-8").strip()


def configured_model() -> str | OpenAIChatModel:
    """Use direct OpenAI when configured, or the repository's Portkey gateway."""
    portkey_key = os.getenv("PORTKEY_API_KEY")
    if portkey_key:
        client = AsyncOpenAI(
            api_key=portkey_key,
            base_url=os.getenv("PORTKEY_BASE_URL", "https://api.portkey.ai/v1"),
            default_headers={
                "x-portkey-api-key": portkey_key,
                "x-portkey-provider": "openai",
            },
        )
        return OpenAIChatModel(MODEL_NAME, provider=OpenAIProvider(openai_client=client))
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        return f"openai:{MODEL_NAME}"
    return f"openai:{MODEL_NAME}"

shop_agent = Agent(
    configured_model(),
    deps_type=ShopDependencies,
    output_type=ChatResponse,
    system_prompt=SYSTEM_PROMPT,
    defer_model_check=True,
)


@shop_agent.tool
def find_products(ctx: RunContext[ShopDependencies], query: str) -> CatalogueSearchResult:
    """Search the Campus Customs catalogue for products matching a shopper's request."""
    return search_catalogue(ctx.deps, query)


@shop_agent.tool
def product_details(ctx: RunContext[ShopDependencies], product_id: str) -> ProductLookup | None:
    """Retrieve complete details and size inventory for one product."""
    return get_product(ctx.deps, product_id)


@shop_agent.tool
def check_stock(ctx: RunContext[ShopDependencies], product_id: str) -> StockResult:
    """Check the real quantity available by size for one catalogue product."""
    return get_stock(ctx.deps, product_id)


@shop_agent.instructions
def customer_context(ctx: RunContext[ShopDependencies]) -> str:
    """Give the agent the authenticated customer's identity and recent memory."""
    if not ctx.deps.user_id:
        return "The shopper is not logged in. Do not claim to know their identity or history."
    history = "\n".join(
        f"{item['role']}: {item['content']}" for item in ctx.deps.chat_history[-10:]
    ) or "No previous chat history is available."
    return (
        f"The authenticated shopper is {ctx.deps.customer_name} "
        f"({ctx.deps.customer_email}), user ID {ctx.deps.user_id}. "
        "Use this identity to make the conversation feel continuous, but do not reveal "
        "private account details unless the shopper asks about their own account. "
        f"Recent conversation memory:\n{history}"
    )


@shop_agent.instructions
def page_context(ctx: RunContext[ShopDependencies]) -> str:
    """Tell the agent which product page the shopper is currently viewing."""
    page = ctx.deps.page_context
    if not page or not page.get("product_id"):
        return "The shopper is not currently viewing a specific product page."
    return (
        "The shopper is currently viewing this exact product page: "
        f"{page.get('name', 'unknown product')} (product_id: {page['product_id']}). "
        "If the shopper says 'this item', 'this', or asks about a color or size without naming a product, "
        "use this product_id with product_details before answering."
    )
