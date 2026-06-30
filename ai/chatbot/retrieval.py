import pickle
import faiss
import numpy as np

from .config import (
    CHUNKS_PATH,
    INDEX_PATH,
    get_embedding_model,
)


def retrieve(query, k=5):

    with open(CHUNKS_PATH, "rb") as f:
        chunks = pickle.load(f)

    index = faiss.read_index(str(INDEX_PATH))

    model = get_embedding_model()

    q_vector = model.encode(
        ["query: " + query]
    )

    q_vector = np.array(
        q_vector,
        dtype="float32"
    )

    faiss.normalize_L2(q_vector)

    _, indices = index.search(
        q_vector,
        k
    )

    results = []

    for idx in indices[0]:

        if idx == -1:
            continue

        results.append(
            chunks[idx]
        )

    return results