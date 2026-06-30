import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from sentence_transformers import SentenceTransformer

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

BASE_DIR = Path(__file__).resolve().parent

CHUNKS_PATH = BASE_DIR / "chunks.pkl"
INDEX_PATH = BASE_DIR / "faiss_index.bin"

EMBED_MODEL = "intfloat/multilingual-e5-large"

api_key = os.getenv("GROQ_API_KEY")

print("GROQ_API_KEY loaded:", api_key is not None)

client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1",
)

_model = None


def get_embedding_model():
    global _model

    if _model is None:
        _model = SentenceTransformer(EMBED_MODEL)

    return _model