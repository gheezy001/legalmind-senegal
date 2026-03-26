"""
LegalMind Sénégal — JOUR 3 : Script principal
Lance l'interface Streamlit et le serveur WhatsApp

Usage :
    python run_jour3.py              # Streamlit (interface web)
    python run_jour3.py --whatsapp   # Serveur WhatsApp uniquement
    python run_jour3.py --both       # Les deux en parallèle
    python run_jour3.py --deploy     # Prépare le déploiement HuggingFace
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path
from loguru import logger

logger.remove()
logger.add(sys.stderr, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")
Path("./logs").mkdir(exist_ok=True)


def lancer_streamlit():
    logger.info("Démarrage interface Streamlit...")
    logger.info("URL : http://localhost:8501")
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.port", "8501",
        "--server.address", "0.0.0.0",
        "--browser.gatherUsageStats", "false",
        "--theme.primaryColor", "#00853F",
        "--theme.backgroundColor", "#ffffff",
        "--theme.secondaryBackgroundColor", "#f8f9fa",
    ])


def lancer_whatsapp():
    logger.info("Démarrage serveur WhatsApp FastAPI...")
    logger.info("URL : http://localhost:8000")
    logger.info("Webhook : POST http://localhost:8000/webhook/whatsapp")
    logger.info("Exposer avec : ngrok http 8000")
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "whatsapp_webhook:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload",
    ])


def lancer_les_deux():
    """Lance Streamlit et WhatsApp en parallèle."""
    import threading
    t1 = threading.Thread(target=lancer_streamlit, daemon=True)
    t2 = threading.Thread(target=lancer_whatsapp, daemon=True)
    t1.start()
    t2.start()
    logger.info("✅ Streamlit : http://localhost:8501")
    logger.info("✅ WhatsApp  : http://localhost:8000")
    try:
        t1.join()
        t2.join()
    except KeyboardInterrupt:
        logger.info("Arrêt des services")


def preparer_deploiement_hf():
    """Prépare les fichiers pour HuggingFace Spaces."""
    logger.info("Préparation déploiement HuggingFace Spaces...")

    # Dockerfile
    dockerfile = """FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p data/raw data/processed data/embeddings/chroma_db logs

EXPOSE 7860

CMD ["streamlit", "run", "app.py", \\
     "--server.port=7860", \\
     "--server.address=0.0.0.0", \\
     "--browser.gatherUsageStats=false"]
"""
    Path("Dockerfile").write_text(dockerfile)

    # Requirements allégés pour HF Spaces
    req_hf = """streamlit==1.36.0
anthropic==0.31.1
chromadb==0.5.3
sentence-transformers==3.0.1
loguru==0.7.2
python-dotenv==1.0.1
pdfplumber==0.11.1
"""
    Path("requirements_hf.txt").write_text(req_hf)

    # README HuggingFace
    readme_hf = """---
title: LegalMind Sénégal
emoji: ⚖️
colorFrom: green
colorTo: blue
sdk: streamlit
sdk_version: 1.36.0
app_file: app.py
pinned: false
license: mit
---

# LegalMind Sénégal — Agent IA Juridique

Assistant juridique IA spécialisé en droit sénégalais et OHADA.

## Fonctionnalités
- Chat juridique avec citations des textes de loi
- Calcul automatique d'indemnités et délais
- Couverture : OHADA, droit du travail, famille, foncier, données personnelles
- Disponible en français (wolof prévu)

## Sources
OHADA · Code Travail SN · Code Famille · Code Pénal · Loi CDP
"""
    Path("README_HF.md").write_text(readme_hf)

    logger.success("Fichiers de déploiement créés :")
    logger.info("  Dockerfile")
    logger.info("  requirements_hf.txt")
    logger.info("  README_HF.md")
    logger.info("\nPour déployer :")
    logger.info("  huggingface-cli login")
    logger.info("  huggingface-cli repo create legalmind-senegal --type space --space_sdk streamlit")
    logger.info("  git push origin main")


def main():
    parser = argparse.ArgumentParser(description="LegalMind Sénégal — Jour 3")
    parser.add_argument("--whatsapp", action="store_true", help="Serveur WhatsApp uniquement")
    parser.add_argument("--both", action="store_true", help="Streamlit + WhatsApp")
    parser.add_argument("--deploy", action="store_true", help="Préparer déploiement HF")
    args = parser.parse_args()

    print("\n" + "="*60)
    print("  LEGALMIND SÉNÉGAL — JOUR 3 COMPLET")
    print("="*60)

    if args.deploy:
        preparer_deploiement_hf()
    elif args.whatsapp:
        lancer_whatsapp()
    elif args.both:
        lancer_les_deux()
    else:
        lancer_streamlit()


if __name__ == "__main__":
    main()
