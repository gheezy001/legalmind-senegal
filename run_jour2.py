"""
LegalMind Sénégal — JOUR 2 : Script principal
Agent complet : RAG + LLM + Calculs juridiques + Évaluation

Usage :
    python run_jour2.py              # Mode interactif CLI
    python run_jour2.py --demo       # Questions de démonstration
    python run_jour2.py --eval       # Évaluation qualité complète
    python run_jour2.py --calcul     # Tests calculs juridiques
"""

import sys
import argparse
from pathlib import Path
from loguru import logger

logger.remove()
logger.add(sys.stderr, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")
logger.add("./logs/jour2.log", rotation="10 MB")
Path("./logs").mkdir(exist_ok=True)


def demo_calculs():
    """Démontre les calculs juridiques sans API."""
    from src.tools.calcul_juridique import (
        calculer_indemnite_licenciement,
        calculer_preavis,
        calculer_cout_creation_entreprise,
        calculer_prescription,
    )

    print("\n" + "🧮 " * 20)
    print("DÉMONSTRATION — Calculs juridiques sénégalais")
    print("🧮 " * 20)

    cas_tests = [
        ("Indemnité — 8 ans, 300 000 FCFA",
         lambda: calculer_indemnite_licenciement(300_000, 8)),
        ("Indemnité — 12 ans, 500 000 FCFA",
         lambda: calculer_indemnite_licenciement(500_000, 12)),
        ("Préavis CDI — 4 ans d'ancienneté",
         lambda: calculer_preavis(4, "cdi")),
        ("Préavis CDI — 7 ans d'ancienneté",
         lambda: calculer_preavis(7, "cdi")),
        ("Création SARL",
         lambda: calculer_cout_creation_entreprise("sarl")),
        ("Création SA",
         lambda: calculer_cout_creation_entreprise("sa")),
        ("Prescription licenciement abusif",
         lambda: calculer_prescription("licenciement_abusif")),
    ]

    for titre, fn in cas_tests:
        print(f"\n{'─'*60}")
        print(f"📋 {titre}")
        print("─"*60)
        resultat = fn()
        print(resultat.formater())


def demo_agent():
    """Démontre l'agent complet avec quelques questions."""
    from src.agent.agent import LegalMindAgent

    agent = LegalMindAgent()

    print("\n" + "⚖️  " * 15)
    print("LÉGALMIND SÉNÉGAL — DÉMONSTRATION AGENT")
    print(f"Statut : {agent.statut()}")
    print("⚖️  " * 15)

    questions_demo = [
        "Comment créer une SARL au Sénégal ?",
        "Calcule l'indemnité de licenciement pour 8 ans d'ancienneté et un salaire de 350 000 FCFA",
        "Quel est le délai de préavis pour un CDI avec 6 ans d'ancienneté ?",
        "Quelle est la différence entre titre foncier et permis d'habiter ?",
    ]

    for question in questions_demo:
        rep = agent.repondre(question)
        rep.afficher()
        print()


def mode_interactif():
    """Mode chat interactif en CLI."""
    from src.agent.agent import LegalMindAgent

    agent = LegalMindAgent()

    print("\n" + "="*60)
    print("  LEGALMIND SÉNÉGAL — Assistant Juridique IA")
    print(f"  Statut API : {'✅ Connectée' if agent.client else '⚠️  Mode simulation'}")
    print(f"  Base RAG   : {agent.retriever.statut()['total']} chunks")
    print("="*60)
    print("Commandes : 'quitter' pour sortir | 'reset' pour effacer l'historique\n")

    while True:
        try:
            question = input("Votre question juridique : ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nAu revoir !")
            break

        if not question:
            continue
        if question.lower() in ["quitter", "exit", "q"]:
            print("Au revoir !")
            break
        if question.lower() == "reset":
            agent.reinitialiser_historique()
            print("✅ Historique effacé\n")
            continue

        rep = agent.repondre(question)
        rep.afficher()


def mode_evaluation():
    """Lance l'évaluation complète de l'agent."""
    from src.agent.agent import LegalMindAgent
    from src.agent.evaluation import evaluer_agent

    logger.info("Démarrage de l'évaluation...")
    agent = LegalMindAgent()
    rapport = evaluer_agent(agent)

    if rapport:
        print(f"\n🎯 Score global : {rapport['score_global_moyen']:.1%}")
        print(f"📚 Sources RAG  : {rapport['taux_sources_citees']:.1%}")
        print(f"⚖️  Articles cités: {rapport['taux_articles_cites']:.1%}")
        print(f"⏱️  Durée moyenne : {rapport['duree_moyenne_s']:.1f}s")


def main():
    parser = argparse.ArgumentParser(description="LegalMind Sénégal — Jour 2")
    parser.add_argument("--demo", action="store_true", help="Questions de démonstration")
    parser.add_argument("--eval", action="store_true", help="Évaluation qualité")
    parser.add_argument("--calcul", action="store_true", help="Tests calculs juridiques")
    args = parser.parse_args()

    if args.calcul:
        demo_calculs()
    elif args.demo:
        demo_agent()
    elif args.eval:
        mode_evaluation()
    else:
        mode_interactif()

    print("\n📋 Jour 3 → python run_jour3.py  (Interface Streamlit + WhatsApp)")


if __name__ == "__main__":
    main()
