import json
from langchain_core.tools import tool
from loguru import logger
from src.database.chroma_db import get_menu_db
from src.models.menu import MenuItem


def _relevance_score(query: str, item: MenuItem) -> float:
    q = query.lower()
    text = f"{item.name} {item.description} {item.category}".lower()
    query_words = [w for w in q.split() if len(w) > 2]
    hits = sum(1 for w in query_words if w in text)
    return hits / max(len(query_words), 1)


@tool
def search_menu_tool(query: str) -> str:
    """
    Search the restaurant menu by any natural language query.
    Returns matching items WITH mandatory choices and add-ons details.
    Use whenever the user mentions food, asks what's available, or wants to order.
    """
    try:
        db = get_menu_db()
        items = db.search(query, n_results=5)

        if not items:
            return json.dumps({"status": "not_found", "message": f"No items found for '{query}'.", "items": []})

        relevant = [i for i in items if _relevance_score(query, i) > 0.0] or items[:3]

        result = {"status": "found", "query": query, "count": len(relevant), "items": []}
        for item in relevant:
            result["items"].append({
                "id": item.id,
                "name": item.name,
                "category": item.category,
                "base_price": item.base_price,
                "description": item.description,
                "mandatory_choices": [
                    {"name": c.name, "required": True,
                     "options": [{"label": o.label, "extra_price": o.extra_price} for o in c.options]}
                    for c in item.mandatory_choices
                ],
                "addons": [{"name": a.name, "price": a.price} for a in item.addons],
                "has_mandatory_choices": len(item.mandatory_choices) > 0,
                "has_addons": len(item.addons) > 0,
            })
        return json.dumps(result, indent=2)

    except Exception as e:
        logger.error(f"Menu search error: {e}")
        return json.dumps({"status": "error", "message": str(e)})


@tool
def validate_order_item(item_id: str, chosen_options: str, chosen_addons: str = "") -> str:
    """
    Validate a customer's order item — check mandatory choices are complete and calculate total price.
    Call this AFTER collecting all mandatory choices from the customer.

    Args:
        item_id: Item ID from search results (e.g. "burger-001")
        chosen_options: JSON string of chosen mandatory options. Example: '{"Size": "Double", "Bun": "Brioche"}'
        chosen_addons: JSON string list of chosen add-on names. Example: '["Extra Cheese", "Bacon"]'

    Returns: valid status, missing choices if any, total price, and order summary.
    """
    from src.data.menu_data import MENU_ITEMS

    item = next((i for i in MENU_ITEMS if i.id == item_id), None)
    if not item:
        return json.dumps({"valid": False, "error": f"Item '{item_id}' not found."})

    try:
        options = json.loads(chosen_options) if chosen_options else {}
    except Exception:
        options = {}

    try:
        addons = json.loads(chosen_addons) if chosen_addons else []
    except Exception:
        addons = []

    # Check mandatory choices — report what's missing
    missing = [
        {"choice": c.name, "options": [o.label for o in c.options]}
        for c in item.mandatory_choices
        if c.name not in options
    ]

    if missing:
        return json.dumps({
            "valid": False,
            "item_name": item.name,
            "missing_choices": missing,
            "message": f"Still need to choose: {', '.join(m['choice'] for m in missing)}"
        })

    # Calculate total
    total = item.base_price
    for choice in item.mandatory_choices:
        for opt in choice.options:
            if opt.label == options.get(choice.name):
                total += opt.extra_price

    addon_details = []
    for addon_name in addons:
        addon = next((a for a in item.addons if a.name == addon_name), None)
        if addon:
            total += addon.price
            addon_details.append(f"{addon.name} (+${addon.price:.2f})")

    return json.dumps({
        "valid": True,
        "item_id": item_id,
        "item_name": item.name,
        "chosen_options": options,
        "chosen_addons": addons,
        "total_price": round(total, 2),
        "summary": (
            f"{item.name} | "
            f"{', '.join(f'{k}: {v}' for k, v in options.items())} | "
            f"Add-ons: {', '.join(addon_details) if addon_details else 'None'} | "
            f"Total: ${total:.2f}"
        )
    })


@tool
def get_menu_categories() -> str:
    """Get all available food categories. Use when user asks what types of food are available."""
    from src.data.menu_data import MENU_ITEMS
    from collections import Counter
    counts = Counter(item.category for item in MENU_ITEMS)
    return "Available: " + ", ".join(f"{cat} ({n})" for cat, n in sorted(counts.items()))
