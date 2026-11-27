import re
import unicodedata


def normalizar(texto: str) -> str:
    """Minúsculas, sin tildes y con espacios simples (para búsquedas y comparaciones)."""
    sin_tildes = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", sin_tildes.lower()).strip()
