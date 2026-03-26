# LegalMind Sénégal — Agent IA Juridique

Agent IA juridique spécialisé en droit sénégalais et OHADA.
Système RAG + Transfer Learning + Fine-tuning Mistral 7B.

## Structure du projet

```
legalmind/
├── data/
│   ├── raw/                    # Documents juridiques bruts (PDFs, TXTs)
│   ├── processed/              # Chunks JSON + dataset fine-tuning
│   └── embeddings/
│       ├── chroma_db/          # Base vectorielle ChromaDB
│       └── modele_affine/      # Modèle embeddings après transfer learning
├── scripts/
│   ├── 01_collecter_documents.py    # Téléchargement docs juridiques
│   ├── 02_traiter_documents.py      # Chunking sémantique par article
│   ├── 03_indexer_chroma.py         # Transfer Learning + ChromaDB
│   ├── 04_generer_dataset.py        # Dataset fine-tuning JSONL
│   └── 05_finetuning_lora.py        # Script LoRA Mistral 7B (Colab)
├── src/
│   ├── rag/                    # Pipeline RAG
│   ├── agent/                  # Agent orchestrateur (Jour 2)
│   ├── tools/                  # Outils calcul juridique (Jour 2)
│   └── utils/                  # Utilitaires communs
├── run_jour1.py                # Lance tout le pipeline Jour 1
├── run_jour2.py                # Agent + LLM (Jour 2)
├── run_jour3.py                # Interface + WhatsApp (Jour 3)
├── app.py                      # Application Streamlit (Jour 3)
├── requirements.txt
└── .env.example
```

## Démarrage rapide — Jour 1

```bash
# 1. Cloner et configurer
git clone https://github.com/vous/legalmind-senegal
cd legalmind-senegal

# 2. Environnement Python
python -m venv .venv
source .venv/bin/activate          # Linux/Mac
# .venv\Scripts\activate           # Windows

# 3. Dépendances
pip install -r requirements.txt

# 4. Configuration
cp .env.example .env
# Éditer .env : ajouter ANTHROPIC_API_KEY

# 5. Lancer le pipeline Jour 1
python run_jour1.py

# Options :
python run_jour1.py --no-download  # Si docs déjà téléchargés
python run_jour1.py --no-tl        # Sans transfer learning (plus rapide)
python run_jour1.py --reset        # Réinitialiser ChromaDB
```

## Sources juridiques indexées

| Source | Domaine | Disponibilité |
|--------|---------|---------------|
| OHADA (ohada.com) | Actes uniformes, CCJA | Gratuit en ligne |
| Code du travail SN | Contrats, licenciement | PDF ILO |
| Code de la famille SN | Mariage, succession | PDF WIPO |
| Code pénal SN | Infractions, peines | PDF WIPO |
| Journal Officiel SN | Lois, décrets | journalofficiel.gouv.sn |
| CDP Sénégal | Protection données | cdp.sn |

## Stack technique

- **RAG** : LlamaIndex + ChromaDB
- **Embeddings** : CamemBERT (affiné par transfer learning)
- **LLM** : Claude API (MVP) → Mistral 7B fine-tuné (phase 2)
- **Fine-tuning** : LoRA via PEFT + TRL (Google Colab Pro)
- **Interface** : Streamlit + WhatsApp Business API
- **Hébergement** : HuggingFace Spaces ou OVH

## Fine-tuning Mistral 7B (après le sprint)

```bash
# 1. Générer le dataset
python scripts/04_generer_dataset.py

# 2. Générer le script Colab
python scripts/05_finetuning_lora.py

# 3. Ouvrir notebooks/finetuning_colab.py dans Google Colab Pro
# 4. Choisir GPU A100 — Durée : ~10h
```

## Partenaires potentiels

- UCAD — Faculté de Droit (Dakar)
- Barreau de Dakar
- OHADA Sénégal
- Jokkolabs Dakar

---
*Ce projet est à des fins de recherche et d'assistance juridique générale.
Il ne remplace pas le conseil d'un avocat qualifié.*
