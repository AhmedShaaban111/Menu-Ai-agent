"""Run this once to load the menu into ChromaDB."""
import sys
sys.path.insert(0, ".")

from src.database.chroma_db import MenuVectorDB
from src.data.menu_data import MENU_ITEMS

if __name__ == "__main__":
    print("🍽️  Ingesting menu items into ChromaDB...")
    db = MenuVectorDB()
    count = db.ingest(MENU_ITEMS)
    print(f"✅ Done! Ingested {count} items.")
    print(f"📊 Total in DB: {db.count()}")

    # Test a quick search
    print("\n🔍 Test search: 'spicy chicken'")
    results = db.search("spicy chicken", n_results=2)
    for item in results:
        print(f"  → {item.name} (${item.base_price})")
