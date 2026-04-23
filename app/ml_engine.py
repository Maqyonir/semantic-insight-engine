from sentence_transformers import SentenceTransformer


class MLEngine:
    """
    A class to handle text embedding generation using SentenceTransformers.

    Attributes:
        model (SentenceTransformer): The model used to generate text embeddings.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        """
        Initializes the MLEngine with a specific pre-trained model.

        Args:
            model_name (str): The name of the SentenceTransformer model. Defaults to "all-MiniLM-L6-v2".
        """
        self.model = SentenceTransformer(model_name_or_path=model_name)

    def create_embedding(self, text: str) -> list[float]:
        """
        Converts a text string into a numerical embedding vector.

        Args:
            text (str): The input text to process.

        Returns:
            list[float]: A list of floatting-point number representing the text embedding.
        """
        return self.model.encode(text).tolist()
