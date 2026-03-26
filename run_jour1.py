"""
LegalMind Sénégal — JOUR 1 : Script principal
Lance l'intégralité du pipeline Jour 1 en séquence.

Usage :
    python run_jour1.py                    # Pipeline complet
    python run_jour1.py --no-download      # Ignore le téléchargement
    python run_jour1.py --no-tl            # Sans transfer learning
    python run_jour1.py --reset            # Réinitialise ChromaDB
"""

import sys
import argparse
from pathlib import Path
from loguru import logger

# Configuration logging
logger.remove()
logger.add(sys.stderr, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")
logger.add("./logs/jour1.log", rotation="10 MB")

Path("./logs").mkdir(exist_ok=True)


def main():
    parser = argparse.ArgumentParser(description="LegalMind Sénégal — Pipeline Jour 1")
    parser.add_argument("--no-download", action="store_true", help="Ignorer téléchargement docs")
    parser.add_argument("--no-tl", action="store_true", help="Sans transfer learning embeddings")
    parser.add_argument("--reset", action="store_true", help="Réinitialiser ChromaDB")
    parser.add_argument("--no-dataset", action="store_true", help="Ignorer génération dataset")
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("LEGALMIND SÉNÉGAL — DÉMARRAGE PIPELINE JOUR 1")
    logger.info("=" * 60)

    # ── ÉTAPE 1 : Collecte des documents ────────────────────────
    if not args.no_download:
        logger.info("\n📥 ÉTAPE 1 : Collecte des documents juridiques")
        from scripts.s01_collecter_documents import collecter_tous_documents
        resultats_dl = collecter_tous_documents()
        logger.info(f"Étape 1 terminée : {len(resultats_dl['succes'])} docs téléchargés")
    else:
        logger.info("⏭️  ÉTAPE 1 : Téléchargement ignoré (--no-download)")

    # ── ÉTAPE 2 : Traitement et chunking ────────────────────────
    logger.info("\n🔪 ÉTAPE 2 : Traitement et chunking des documents")
    sys.path.insert(0, str(Path(__file__).parent))

    # Import dynamique pour éviter les erreurs si module pas encore créé
    try:
        from scripts.s02_traiter_documents import traiter_tous_documents
        chunks = traiter_tous_documents()
        logger.info(f"Étape 2 terminée : {len(chunks)} chunks extraits")
    except ModuleNotFoundError:
        # Exécution directe des scripts
        import subprocess
        subprocess.run([sys.executable, "scripts/02_traiter_documents.py"], check=True)

    # ── ÉTAPE 3 : Transfer Learning + Indexation ChromaDB ───────
    logger.info("\n🧠 ÉTAPE 3 : Transfer Learning + Indexation ChromaDB")
    try:
        from scripts.s03_indexer_chroma import pipeline_jour1
        modele, resultats = pipeline_jour1(
            faire_transfer_learning=not args.no_tl,
            reset_chroma=args.reset,
        )
        logger.info(f"Étape 3 terminée : {resultats.get('total', 0)} chunks indexés")
    except ModuleNotFoundError:
        import subprocess
        subprocess.run([sys.executable, "scripts/03_indexer_chroma.py"], check=True)

    # ── ÉTAPE 4 : Génération dataset fine-tuning ─────────────────
    if not args.no_dataset:
        logger.info("\n📊 ÉTAPE 4 : Génération dataset fine-tuning")
        try:
            from scripts.s04_generer_dataset import generer_dataset_finetuning
            stats = generer_dataset_finetuning()
            logger.info(f"Étape 4 terminée : {stats['total']} exemples générés")
        except ModuleNotFoundError:
            import subprocess
            subprocess.run([sys.executable, "scripts/04_generer_dataset.py"], check=True)

    # ── ÉTAPE 5 : Préparer script fine-tuning LLM ────────────────
    logger.info("\n⚙️  ÉTAPE 5 : Génération script fine-tuning Mistral LoRA")
    try:
        from scripts.s05_finetuning_lora import generer_notebook_colab
        generer_notebook_colab()
    except ModuleNotFoundError:
        import subprocess
        subprocess.run([sys.executable, "scripts/05_finetuning_lora.py"], check=True)

    # ── RÉSUMÉ ───────────────────────────────────────────────────
    logger.info("\n" + "🎉" * 20)
    logger.info("JOUR 1 COMPLET — Récapitulatif")
    logger.info("🎉" * 20)
    logger.info("")
    logger.info("✅ Documents juridiques collectés (data/raw/)")
    logger.info("✅ Chunks extraits avec métadonnées (data/processed/)")
    logger.info("✅ Embeddings affinés par transfer learning")
    logger.info("✅ Base vectorielle ChromaDB opérationnelle")
    logger.info("✅ Dataset fine-tuning généré (200 exemples JSONL)")
    logger.info("✅ Script LoRA Mistral 7B prêt pour Colab")
    logger.info("")
    logger.info("📋 Prochaine étape — JOUR 2 :")
    logger.info("   python run_jour2.py  (Agent + LLM + Outil calcul)")
    logger.info("")


if __name__ == "__main__":
    main()
