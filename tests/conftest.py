import os
import tempfile

# Configurar o banco de testes antes de importar a API
banco_temporario = tempfile.TemporaryDirectory()

os.environ["RAIZES_DB"] = os.path.join(
    banco_temporario.name,
    "raizes_teste.db"
)

from main import app  # noqa: E402