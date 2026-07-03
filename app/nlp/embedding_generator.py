import json
import numpy as np

from sentence_transformers import SentenceTransformer


class EmbeddingGenerator:

    def __init__(self):

        self.model = SentenceTransformer(
            "BAAI/bge-base-en-v1.5"
        )

    def generate_embedding(self, text):

        if text is None:
            return None

        text = text.strip()

        if len(text) == 0:
            return None

        embedding = self.model.encode(

            text,

            normalize_embeddings=True,

            convert_to_numpy=True

        )

        return embedding

    def embedding_to_json(self, embedding):

        if embedding is None:
            return None

        return json.dumps(
            embedding.tolist()
        )

    def json_to_embedding(self, embedding_json):

        if embedding_json is None:
            return None

        return np.array(
            json.loads(
                embedding_json
            )
        )