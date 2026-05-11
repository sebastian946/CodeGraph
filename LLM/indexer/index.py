import numpy as np
from redis.commands.search.field import TextField, VectorField, TagField
from redis.commands.search.index_definition import IndexDefinition, IndexType
from redis.exceptions import ResponseError
from config.config import get_redis_client


# Key schema helpers — centralised so every module uses the same format
def chunk_key(repo_id: str, chunk_hash: str) -> str:
    return f"chunk:{repo_id}:{chunk_hash}"


def graph_key(repo_id: str) -> str:
    return f"graph:{repo_id}"


class Indexer:
    INDEX_NAME = "code_index"
    VECTOR_DIM = 1024          # voyage-code-2 output dimension
    KEY_PREFIX = "chunk:"      # FT.CREATE indexes all keys starting with this

    def __init__(self) -> None:
        self.redis_client = get_redis_client()
        self._schema = [
            TextField("content"),
            TextField("filepath"),
            TagField("language"),
            VectorField(
                "embedding",
                "HNSW",
                {
                    "TYPE": "FLOAT32",
                    "DIM": self.VECTOR_DIM,
                    "DISTANCE_METRIC": "COSINE",
                    # M=16: bidirectional links per node; higher = better recall, more RAM
                    "M": 16,
                    # EF_CONSTRUCTION=200: candidate list size at build time;
                    # higher = denser graph (better recall), slower indexing
                    "EF_CONSTRUCTION": 200,
                },
            ),
        ]

    def ensure_index_exists(self) -> bool:
        """Creates the index when it does not exist. Returns True if created."""
        try:
            self.redis_client.ft(self.INDEX_NAME).info()
            return False
        except ResponseError:
            self._create_index()
            return True

    def _create_index(self) -> None:
        definition = IndexDefinition(
            prefix=[self.KEY_PREFIX],
            index_type=IndexType.HASH,
        )
        self.redis_client.ft(self.INDEX_NAME).create_index(
            self._schema,
            definition=definition,
        )

    def add_chunk(
        self,
        repo_id: str,
        chunk_hash: str,
        content: str,
        filepath: str,
        language: str,
        embedding: list[float],
    ) -> None:
        key = chunk_key(repo_id, chunk_hash)
        vector_bytes = np.array(embedding, dtype=np.float32).tobytes()
        self.redis_client.hset(
            key,
            mapping={
                "content": content,
                "filepath": filepath,
                "language": language,
                "repo_id": repo_id,
                "embedding": vector_bytes,
            },
        )
