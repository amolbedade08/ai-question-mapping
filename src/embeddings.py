from sentence_transformers import SentenceTransformer


MODEL_NAME = (
    "sentence-transformers/"
    "all-mpnet-base-v2"
)


_model = None


def get_model():

    global _model

    if _model is None:

        _model = SentenceTransformer(
            MODEL_NAME
        )

    return _model


def encode_texts(texts):

    if not texts:
        return []

    model = get_model()

    return model.encode(
        texts,
        normalize_embeddings=True,
        convert_to_numpy=True
    )