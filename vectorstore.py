import hashlib
import shutil
import threading
from functools import lru_cache
from pathlib import Path

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import RAG_FILES_DIR, VECTOR_STORE_PATH
from embeddings import get_embeddings


# coleção nova: a antiga (OpenAI, 1536 dims) é incompatível com o embedding local (384 dims)
COLLECTION_NAME = 'rag_multilingual'
ALLOWED_EXTENSIONS = {'.pdf', '.txt', '.md'}

_write_lock = threading.RLock()


def _rag_dir() -> Path:
    return Path(RAG_FILES_DIR)


def _processed_dir() -> Path:
    path = _rag_dir() / 'processed'
    path.mkdir(parents=True, exist_ok=True)
    return path


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path):
    if path.suffix.lower() == '.pdf':
        return PyPDFLoader(str(path)).load()
    return TextLoader(str(path), encoding='utf-8').load()


def _split(docs):
    # o MiniLM multilíngue trunca em ~128 tokens: chunks de 1000 chars perderiam o final
    return RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=80).split_documents(docs)


def _ingest(vs: Chroma, path: Path) -> dict:
    file_hash = _file_hash(path)

    if vs.get(where={'file_hash': file_hash}, limit=1)['ids']:
        return {'file': path.name, 'status': 'duplicate', 'chunks': 0}

    docs = _load(path)
    for doc in docs:
        metadata = {'source': path.name, 'file_hash': file_hash}
        if 'page' in doc.metadata:
            metadata['page'] = doc.metadata['page']
        doc.metadata = metadata

    chunks = _split(docs)
    if not chunks:
        raise ValueError('arquivo sem texto extraível')

    vs.delete(where={'source': path.name})  # substitui a versão anterior do mesmo arquivo
    vs.add_documents(chunks)
    return {'file': path.name, 'status': 'indexed', 'chunks': len(chunks)}


def _safe_ingest(vs: Chroma, path: Path) -> dict:
    try:
        return _ingest(vs, path)
    except Exception as error:
        return {'file': path.name, 'status': 'error', 'chunks': 0, 'detail': type(error).__name__}


def _move_pending() -> list[Path]:
    """Move arquivos soltos na raiz de rag_files para processed/."""
    processed = _processed_dir()
    moved = []
    for path in sorted(_rag_dir().iterdir()):
        if path.is_file() and path.suffix.lower() in ALLOWED_EXTENSIONS:
            dest = processed / path.name
            shutil.move(str(path), str(dest))
            moved.append(dest)
    return moved


@lru_cache(maxsize=1)
def get_vectorstore() -> Chroma:
    vs = Chroma(
        embedding_function=get_embeddings(),
        collection_name=COLLECTION_NAME,
        persist_directory=VECTOR_STORE_PATH,
    )
    with _write_lock:
        for path in _move_pending():
            _safe_ingest(vs, path)
    return vs


def ingest_upload(name: str, content: bytes) -> dict:
    dest = _processed_dir() / name
    existed = dest.exists()
    dest.write_bytes(content)

    with _write_lock:
        result = _safe_ingest(get_vectorstore(), dest)

    if result['status'] != 'indexed' and not existed:
        dest.unlink(missing_ok=True)
    return result


def reindex() -> dict:
    with _write_lock:
        vs = get_vectorstore()
        _move_pending()
        vs.reset_collection()
        files = [
            _safe_ingest(vs, path)
            for path in sorted(_processed_dir().iterdir())
            if path.is_file() and path.suffix.lower() in ALLOWED_EXTENSIONS
        ]
    return {'files': files, 'chunks': sum(f['chunks'] for f in files)}