from sentence_transformers import SentenceTransformer
import re


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

    def get_chunks(
        self, text: str, chunk_size: int = 500, overlap: int = 100
    ) -> list[str]:
        if overlap >= chunk_size:
            overlap = chunk_size // 2

        # Try to split the text into sections starting with a number + dot + space.
        sections = re.split(r"\n(?=\d+\.\s)", text)

        chunks = []
        for section in sections:
            section = section.strip()
            if not section:
                continue

            # Divide the section if it's too big.
            if len(section) > chunk_size:
                start = 0
                while start < len(section):
                    # Get a segment of the text.
                    end = start + chunk_size
                    chunk = section[start:end]

                    # Handle the division.
                    if end < len(section):
                        last_space = chunk.rfind(" ")
                        if last_space != -1:
                            chunk = chunk[:last_space]

                    chunks.append(chunk.strip())

                    # Go forward given the overlap.
                    step = len(chunk) - overlap
                    if step <= 0:
                        start += len(chunk)
                    else:
                        start += step

            else:
                # If the section is small enough.
                chunks.append(section.strip())

        return chunks
