import json
import chromadb
from chromadb.utils import embedding_functions
from loguru import logger
from src.models.menu import MenuItem
from src.data.menu_data import MENU_ITEMS


class MenuVectorDB:
    """ChromaDB-based vector store for menu items."""

    COLLECTION_NAME = "menu_items"

    def __init__(self, persist_dir: str = "./chroma_data"):
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        self.collection = self.client.get_or_create_collection(
            name=self.COLLECTION_NAME,
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"},
        )

    def ingest(self, items: list[MenuItem] | None = None) -> int:
        """Ingest menu items into ChromaDB. Returns count of ingested items."""
        items = items or MENU_ITEMS

        # Build rich text for embedding (name + description + category + choices)
        documents, metadatas, ids = [], [], []

        for item in items:
            # Text to embed — richer = better semantic search
            embed_text = (
                f"{item.name}. {item.description}. Category: {item.category}. "
                f"Price: ${item.base_price:.2f}. "
                + " ".join(
                    f"Choose {c.name}: {', '.join(o.label for o in c.options)}."
                    for c in item.mandatory_choices
                )
                + " ".join(f"Add-on: {a.name}." for a in item.addons)
            )

            # Store full item as JSON in metadata
            documents.append(embed_text)
            metadatas.append({"item_json": item.model_dump_json()})
            ids.append(item.id)

        # Upsert (safe to run multiple times)
        self.collection.upsert(documents=documents, metadatas=metadatas, ids=ids)
        logger.info(f"Ingested {len(items)} menu items into ChromaDB")
        return len(items)

    def search(self, query: str, n_results: int = 3) -> list[MenuItem]:
        """Search menu by natural language query. Returns top matching items."""
        results = self.collection.query(
            query_texts=[query],
            n_results=min(n_results, self.collection.count()),
        )

        items = []
        for metadata in results["metadatas"][0]:
            item_data = json.loads(metadata["item_json"])
            items.append(MenuItem(**item_data))

        return items

    def count(self) -> int:
        return self.collection.count()


# Singleton instance
_db_instance: MenuVectorDB | None = None


def get_menu_db() -> MenuVectorDB:
    global _db_instance
    if _db_instance is None:
        _db_instance = MenuVectorDB()
    return _db_instance
