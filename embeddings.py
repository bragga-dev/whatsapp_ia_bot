from functools import lru_cache

from fastembed import TextEmbedding
from langchain_core.embeddings import Embeddings

from config import EMBEDDINGS_CACHE_DIR, EMBEDDINGS_MODEL


class LocalEmbeddings(Embeddings):
    def __init__(self, model_name: str, cache_dir: str):
        self._model = TextEmbedding(model_name=model_name, cache_dir=cache_dir)

    def embed_documents(self, texts):
        return [v.tolist() for v in self._model.embed(texts)]

    def embed_query(self, text):
        return next(iter(self._model.embed([text]))).tolist()


@lru_cache(maxsize=1)
def get_embeddings() -> LocalEmbeddings:
    return LocalEmbeddings(EMBEDDINGS_MODEL, EMBEDDINGS_CACHE_DIR)