from indexer.index import Indexer


def bootstrap() -> None:
    indexer = Indexer()
    created = indexer.ensure_index_exists()
    if created:
        print(f"Index '{Indexer.INDEX_NAME}' created successfully.")
    else:
        print(f"Index '{Indexer.INDEX_NAME}' already exists, skipping.")


if __name__ == "__main__":
    bootstrap()
