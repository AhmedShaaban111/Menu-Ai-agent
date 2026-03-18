from pydantic import BaseModel
from typing import List, Optional


class ChoiceOption(BaseModel):
    label: str           # e.g. "Small", "Medium", "Large"
    extra_price: float = 0.0  # extra cost on top of base price


class MandatoryChoice(BaseModel):
    name: str            # e.g. "Size", "Spice Level"
    options: List[ChoiceOption]


class Addon(BaseModel):
    name: str            # e.g. "Extra Cheese", "Bacon"
    price: float


class MenuItem(BaseModel):
    id: str
    name: str
    description: str
    base_price: float
    category: str        # e.g. "Burger", "Pizza", "Drink"
    mandatory_choices: List[MandatoryChoice] = []
    addons: List[Addon] = []

    def format_for_agent(self) -> str:
        """Format item details to send to LLM."""
        text = f"""
🍽️ {self.name} — ${self.base_price:.2f}
Category: {self.category}
Description: {self.description}
"""
        if self.mandatory_choices:
            text += "\n⚠️ Required Choices:\n"
            for choice in self.mandatory_choices:
                opts = ", ".join(
                    f"{o.label} (+${o.extra_price:.2f})" if o.extra_price > 0 else o.label
                    for o in choice.options
                )
                text += f"  • {choice.name}: [{opts}]\n"

        if self.addons:
            text += "\n✨ Optional Add-ons:\n"
            for addon in self.addons:
                text += f"  • {addon.name} (+${addon.price:.2f})\n"

        return text.strip()
