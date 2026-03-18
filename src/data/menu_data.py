from src.models.menu import MenuItem, MandatoryChoice, ChoiceOption, Addon

MENU_ITEMS: list[MenuItem] = [
    # ── BURGERS ──────────────────────────────────────────────
    MenuItem(
        id="burger-001",
        name="Classic Cheeseburger",
        description="Juicy beef patty with cheddar cheese, lettuce, tomato, and pickles",
        base_price=9.99,
        category="Burger",
        mandatory_choices=[
            MandatoryChoice(name="Size", options=[
                ChoiceOption(label="Single", extra_price=0),
                ChoiceOption(label="Double", extra_price=2.50),
                ChoiceOption(label="Triple", extra_price=5.00),
            ]),
            MandatoryChoice(name="Bun", options=[
                ChoiceOption(label="Sesame", extra_price=0),
                ChoiceOption(label="Brioche", extra_price=0.50),
                ChoiceOption(label="Gluten-Free", extra_price=1.00),
            ]),
        ],
        addons=[
            Addon(name="Extra Cheese", price=0.75),
            Addon(name="Bacon", price=1.50),
            Addon(name="Avocado", price=1.25),
            Addon(name="Caramelized Onions", price=0.75),
        ]
    ),
    MenuItem(
        id="burger-002",
        name="Spicy Crispy Chicken Burger",
        description="Crispy fried chicken with spicy mayo, coleslaw, and jalapeños",
        base_price=10.99,
        category="Burger",
        mandatory_choices=[
            MandatoryChoice(name="Spice Level", options=[
                ChoiceOption(label="Mild", extra_price=0),
                ChoiceOption(label="Medium", extra_price=0),
                ChoiceOption(label="Hot", extra_price=0),
                ChoiceOption(label="Extra Hot", extra_price=0),
            ]),
            MandatoryChoice(name="Bun", options=[
                ChoiceOption(label="Sesame", extra_price=0),
                ChoiceOption(label="Brioche", extra_price=0.50),
            ]),
        ],
        addons=[
            Addon(name="Extra Jalapeños", price=0.50),
            Addon(name="Cheese Slice", price=0.75),
            Addon(name="Pickles", price=0.25),
        ]
    ),
    MenuItem(
        id="burger-003",
        name="Mushroom Swiss Burger",
        description="Beef patty topped with sautéed mushrooms and Swiss cheese",
        base_price=11.49,
        category="Burger",
        mandatory_choices=[
            MandatoryChoice(name="Size", options=[
                ChoiceOption(label="Single", extra_price=0),
                ChoiceOption(label="Double", extra_price=2.50),
            ]),
        ],
        addons=[
            Addon(name="Truffle Sauce", price=1.00),
            Addon(name="Extra Mushrooms", price=0.75),
        ]
    ),

    # ── PIZZA ─────────────────────────────────────────────────
    MenuItem(
        id="pizza-001",
        name="Margherita Pizza",
        description="Classic tomato sauce, fresh mozzarella, and basil leaves",
        base_price=12.99,
        category="Pizza",
        mandatory_choices=[
            MandatoryChoice(name="Size", options=[
                ChoiceOption(label="Small (8\")", extra_price=0),
                ChoiceOption(label="Medium (12\")", extra_price=4.00),
                ChoiceOption(label="Large (16\")", extra_price=7.00),
            ]),
            MandatoryChoice(name="Crust", options=[
                ChoiceOption(label="Thin", extra_price=0),
                ChoiceOption(label="Thick", extra_price=0),
                ChoiceOption(label="Stuffed Crust", extra_price=2.00),
            ]),
        ],
        addons=[
            Addon(name="Extra Mozzarella", price=1.50),
            Addon(name="Olives", price=0.75),
            Addon(name="Mushrooms", price=0.75),
            Addon(name="Pepperoni", price=1.50),
        ]
    ),
    MenuItem(
        id="pizza-002",
        name="BBQ Chicken Pizza",
        description="Smoky BBQ sauce, grilled chicken, red onions, and cilantro",
        base_price=14.99,
        category="Pizza",
        mandatory_choices=[
            MandatoryChoice(name="Size", options=[
                ChoiceOption(label="Small (8\")", extra_price=0),
                ChoiceOption(label="Medium (12\")", extra_price=4.00),
                ChoiceOption(label="Large (16\")", extra_price=7.00),
            ]),
            MandatoryChoice(name="Crust", options=[
                ChoiceOption(label="Thin", extra_price=0),
                ChoiceOption(label="Thick", extra_price=0),
                ChoiceOption(label="Stuffed Crust", extra_price=2.00),
            ]),
        ],
        addons=[
            Addon(name="Extra Chicken", price=2.00),
            Addon(name="Jalapeños", price=0.50),
            Addon(name="Corn", price=0.50),
        ]
    ),

    # ── PASTA ─────────────────────────────────────────────────
    MenuItem(
        id="pasta-001",
        name="Spaghetti Bolognese",
        description="Classic Italian meat sauce with ground beef and tomatoes",
        base_price=13.49,
        category="Pasta",
        mandatory_choices=[
            MandatoryChoice(name="Pasta Type", options=[
                ChoiceOption(label="Spaghetti", extra_price=0),
                ChoiceOption(label="Penne", extra_price=0),
                ChoiceOption(label="Fettuccine", extra_price=0),
            ]),
            MandatoryChoice(name="Size", options=[
                ChoiceOption(label="Regular", extra_price=0),
                ChoiceOption(label="Large", extra_price=2.50),
            ]),
        ],
        addons=[
            Addon(name="Extra Parmesan", price=0.75),
            Addon(name="Garlic Bread", price=1.50),
            Addon(name="Side Salad", price=2.00),
        ]
    ),
    MenuItem(
        id="pasta-002",
        name="Creamy Alfredo Pasta",
        description="Rich and creamy Alfredo sauce with garlic and parmesan",
        base_price=12.99,
        category="Pasta",
        mandatory_choices=[
            MandatoryChoice(name="Protein", options=[
                ChoiceOption(label="No Protein", extra_price=0),
                ChoiceOption(label="Chicken", extra_price=2.50),
                ChoiceOption(label="Shrimp", extra_price=3.50),
                ChoiceOption(label="Salmon", extra_price=4.00),
            ]),
            MandatoryChoice(name="Pasta Type", options=[
                ChoiceOption(label="Fettuccine", extra_price=0),
                ChoiceOption(label="Penne", extra_price=0),
                ChoiceOption(label="Rigatoni", extra_price=0),
            ]),
        ],
        addons=[
            Addon(name="Extra Sauce", price=0.75),
            Addon(name="Mushrooms", price=0.75),
            Addon(name="Spinach", price=0.75),
        ]
    ),

    # ── DRINKS ────────────────────────────────────────────────
    MenuItem(
        id="drink-001",
        name="Fresh Lemonade",
        description="Freshly squeezed lemonade with mint",
        base_price=3.99,
        category="Drink",
        mandatory_choices=[
            MandatoryChoice(name="Size", options=[
                ChoiceOption(label="Small", extra_price=0),
                ChoiceOption(label="Medium", extra_price=1.00),
                ChoiceOption(label="Large", extra_price=2.00),
            ]),
            MandatoryChoice(name="Sweetness", options=[
                ChoiceOption(label="Regular", extra_price=0),
                ChoiceOption(label="Less Sweet", extra_price=0),
                ChoiceOption(label="No Sugar", extra_price=0),
            ]),
        ],
        addons=[
            Addon(name="Extra Mint", price=0.25),
            Addon(name="Strawberry Syrup", price=0.50),
            Addon(name="Ginger Shot", price=0.75),
        ]
    ),
    MenuItem(
        id="drink-002",
        name="Milkshake",
        description="Thick and creamy milkshake made with premium ice cream",
        base_price=5.99,
        category="Drink",
        mandatory_choices=[
            MandatoryChoice(name="Flavor", options=[
                ChoiceOption(label="Chocolate", extra_price=0),
                ChoiceOption(label="Vanilla", extra_price=0),
                ChoiceOption(label="Strawberry", extra_price=0),
                ChoiceOption(label="Oreo", extra_price=0.75),
                ChoiceOption(label="Salted Caramel", extra_price=0.75),
            ]),
            MandatoryChoice(name="Size", options=[
                ChoiceOption(label="Regular", extra_price=0),
                ChoiceOption(label="Large", extra_price=1.50),
            ]),
        ],
        addons=[
            Addon(name="Whipped Cream", price=0.50),
            Addon(name="Extra Scoop", price=1.50),
        ]
    ),

    # ── SIDES ─────────────────────────────────────────────────
    MenuItem(
        id="side-001",
        name="French Fries",
        description="Crispy golden fries seasoned to perfection",
        base_price=3.49,
        category="Side",
        mandatory_choices=[
            MandatoryChoice(name="Size", options=[
                ChoiceOption(label="Small", extra_price=0),
                ChoiceOption(label="Medium", extra_price=1.00),
                ChoiceOption(label="Large", extra_price=2.00),
            ]),
            MandatoryChoice(name="Seasoning", options=[
                ChoiceOption(label="Classic Salt", extra_price=0),
                ChoiceOption(label="Cajun Spice", extra_price=0),
                ChoiceOption(label="Parmesan Herb", extra_price=0.50),
            ]),
        ],
        addons=[
            Addon(name="Cheese Sauce", price=0.75),
            Addon(name="Truffle Oil", price=1.00),
            Addon(name="Sriracha Dip", price=0.50),
        ]
    ),
]
