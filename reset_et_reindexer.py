"""
LegalMind — Script de réindexation complète
Usage : python reset_et_reindexer.py
"""
import sys, os, shutil, importlib.util
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

CHROMA_DIR = os.getenv("CHROMA_DIR", "./data/embeddings/chroma_db")
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
)

def main():
    # 1. Supprimer l'ancienne base
    chroma_path = Path(CHROMA_DIR)
    if chroma_path.exists():
        shutil.rmtree(chroma_path)
        logger.info(f"Base ChromaDB supprimée : {CHROMA_DIR}")
    chroma_path.mkdir(parents=True, exist_ok=True)

    # 2. Charger le modèle
    logger.info(f"Modèle embeddings : {EMBEDDING_MODEL}")
    modele = None
    try:
        from sentence_transformers import SentenceTransformer
        modele = SentenceTransformer(EMBEDDING_MODEL)
        dim = len(modele.encode(["test"])[0])
        logger.success(f"Modèle chargé — dimension : {dim}d")
    except Exception as e:
        logger.warning(f"Modèle non chargé ({e}) — ChromaDB utilisera son modèle interne")

    # 3. Charger le script d'indexation directement
    sys.path.insert(0, ".")
    spec = importlib.util.spec_from_file_location(
        "indexer", "scripts/03_indexer_chroma.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # 4. Réindexer
    resultats = mod.indexer_chunks(
        modele_embeddings=modele,
        reset=False,  # déjà supprimé manuellement ci-dessus
    )
    logger.success(f"Réindexation terminée : {resultats.get('total', 0)} chunks indexés")

if __name__ == "__main__":
    main()
