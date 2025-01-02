from vertexai.preview.language_models import TextEmbeddingModel

MODEL_NAME = "text-embedding-004"

def embed_text(text):
    """Embeds text using the Vertex AI embedding model."""
    model = TextEmbeddingModel.from_pretrained(MODEL_NAME)
    embeddings = model.get_embeddings([text])
    return embeddings[0].values  # Return the embedding vector
