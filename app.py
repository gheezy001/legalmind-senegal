"""
LegalMind Sénégal — Jour 3 · Interface Streamlit
Application web complète : chat juridique + sources + calculs
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from pathlib import Path
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# Configuration de la page
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="LegalMind Sénégal",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS personnalisé
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
/* Couleurs principales */
:root {
    --vert-senegal: #00853F;
    --jaune-senegal: #FDEF42;
    --rouge-senegal: #E31E24;
    --bleu-juridique: #1a3a5c;
    --gris-clair: #f8f9fa;
}

/* Header principal */
.header-legalmind {
    background: linear-gradient(135deg, #1a3a5c 0%, #00853F 100%);
    padding: 1.5rem 2rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
    color: white;
}
.header-legalmind h1 { color: white; font-size: 2rem; margin: 0; }
.header-legalmind p { color: rgba(255,255,255,0.85); margin: 0.3rem 0 0 0; font-size: 1rem; }

/* Badges domaine */
.badge-domaine {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-right: 6px;
}
.badge-ohada    { background: #e8f4fd; color: #1a6ba0; }
.badge-travail  { background: #e8f6ef; color: #1a7a45; }
.badge-famille  { background: #fef3e2; color: #b36a00; }
.badge-foncier  { background: #f3e8fd; color: #6a1ab3; }
.badge-penal    { background: #fde8e8; color: #b31a1a; }
.badge-general  { background: #f0f0f0; color: #555; }

/* Carte source */
.source-card {
    background: #f8f9fa;
    border-left: 3px solid #00853F;
    padding: 8px 12px;
    margin: 4px 0;
    border-radius: 0 6px 6px 0;
    font-size: 0.85rem;
}

/* Carte calcul */
.calcul-card {
    background: #fff8e1;
    border: 1px solid #ffc107;
    padding: 12px 16px;
    border-radius: 8px;
    margin: 8px 0;
}

/* Message chat */
.chat-message-user {
    background: #e8f4fd;
    padding: 12px 16px;
    border-radius: 12px 12px 4px 12px;
    margin: 8px 0;
    max-width: 85%;
    margin-left: auto;
}
.chat-message-assistant {
    background: white;
    border: 1px solid #e0e0e0;
    padding: 12px 16px;
    border-radius: 4px 12px 12px 12px;
    margin: 8px 0;
    max-width: 90%;
}

/* Disclaimer */
.disclaimer {
    background: #fff3cd;
    border: 1px solid #ffc107;
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 0.8rem;
    color: #856404;
    margin-top: 12px;
}

/* Métriques */
.metric-mini {
    text-align: center;
    padding: 8px;
    background: #f8f9fa;
    border-radius: 8px;
}
.metric-mini .val { font-size: 1.4rem; font-weight: 700; color: #1a3a5c; }
.metric-mini .lab { font-size: 0.7rem; color: #888; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Initialisation de l'agent (mise en cache)
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_resource(show_spinner="Chargement de l'agent juridique...")
def charger_agent():
    from src.rag.retriever import LegalRetriever
    from src.agent.agent import LegalMindAgent
    retriever = LegalRetriever()
    return LegalMindAgent(retriever=retriever)


# ─────────────────────────────────────────────────────────────────────────────
# État de la session
# ─────────────────────────────────────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []
if "nb_questions" not in st.session_state:
    st.session_state.nb_questions = 0
if "domaine_filtre" not in st.session_state:
    st.session_state.domaine_filtre = None


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### ⚖️ LegalMind Sénégal")
    st.markdown("*Agent IA juridique — Droit SN + OHADA*")
    st.divider()

    # Statut système
    agent = charger_agent()
    statut = agent.statut()

    api_ok = statut["api_configuree"]
    rag_total = statut["rag"]["total"]

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""<div class="metric-mini">
            <div class="val">{'✅' if api_ok else '⚠️'}</div>
            <div class="lab">API LLM</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="metric-mini">
            <div class="val">{rag_total}</div>
            <div class="lab">Chunks RAG</div>
        </div>""", unsafe_allow_html=True)

    if not api_ok:
        st.warning("Ajoutez ANTHROPIC_API_KEY dans .env", icon="🔑")

    st.divider()

    # Filtre domaine
    st.markdown("**Domaine juridique**")
    domaine_options = {
        "🔍 Tous les domaines": None,
        "🏢 Droit des affaires (OHADA)": "ohada",
        "👷 Droit du travail": "travail",
        "👨‍👩‍👧 Droit de la famille": "famille",
        "🏠 Droit foncier": "foncier",
        "⚖️ Droit pénal": "penal",
        "🔒 Protection des données": "donnees",
    }
    choix_domaine = st.selectbox("Filtrer par domaine", list(domaine_options.keys()), index=0)
    st.session_state.domaine_filtre = domaine_options[choix_domaine]

    st.divider()

    # Sélecteur de langue
    st.markdown("**Langue / Làkk**")
    langue_ui = st.radio(
        "Choisir la langue",
        ["🇫🇷 Français", "🇸🇳 Wolof"],
        horizontal=True,
        label_visibility="collapsed",
    )
    st.session_state.langue_ui = "wolof" if "Wolof" in langue_ui else "francais"

    if st.session_state.get("langue_ui") == "wolof":
        st.info("Mode wolof activé — vos questions seront traduites automatiquement")

    st.divider()

    # Questions rapides
    st.markdown("**Questions fréquentes**")
    if st.session_state.get("langue_ui") == "wolof":
        questions_rapides = [
            "Naka la tax liggéey bi ?",
            "Xaalis u liggéey bi naka la ?",
            "Lan la tax société bi ?",
            "Kër gi ak titre foncier ?",
            "Diisoo bi naka la ?",
            "Données personnelles yi ?",
        ]
    else:
        questions_rapides = [
            "Comment créer une SARL ?",
            "Calcul indemnité licenciement 5 ans, 250 000 FCFA",
            "Délai préavis CDI 3 ans ancienneté",
            "Titre foncier vs permis d'habiter",
            "Règles succession sans testament",
            "Obligations protection données CDP",
        ]
    for qr in questions_rapides:
        if st.button(qr, use_container_width=True, key=f"qr_{qr[:20]}"):
            st.session_state.question_rapide = qr

    st.divider()

    # Contrôles
    col_r, col_e = st.columns(2)
    with col_r:
        if st.button("🗑️ Effacer", use_container_width=True):
            st.session_state.messages = []
            st.session_state.nb_questions = 0
            agent.reinitialiser_historique()
            st.rerun()
    with col_e:
        if st.button("📊 Évaluer", use_container_width=True):
            st.session_state.run_eval = True

    st.divider()
    st.markdown("""
    <small>
    📚 Sources : OHADA · Code Travail SN · Code Famille · Code Pénal · CDP<br>
    ⚠️ <em>Information générale — consultez un avocat pour votre situation</em>
    </small>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Zone principale
# ─────────────────────────────────────────────────────────────────────────────

# Header
st.markdown("""
<div class="header-legalmind">
    <h1>⚖️ LegalMind Sénégal</h1>
    <p>Assistant IA juridique — Droit sénégalais · OHADA · Calculs automatiques</p>
</div>
""", unsafe_allow_html=True)

# Onglets
tab_chat, tab_calcul, tab_docs = st.tabs(["💬 Chat juridique", "🧮 Calculateur", "📚 Documents indexés"])

# ─────────────────────────────────────────────────────────────────────────────
# Onglet 1 : Chat
# ─────────────────────────────────────────────────────────────────────────────

with tab_chat:

    # Afficher l'historique
    if not st.session_state.messages:
        st.markdown("""
        <div style="text-align:center; padding: 2rem; color: #888;">
            <div style="font-size: 3rem;">⚖️</div>
            <h3 style="color: #1a3a5c;">Bonjour ! Je suis LegalMind.</h3>
            <p>Posez-moi une question sur le droit sénégalais ou l'OHADA.<br>
            Je cite toujours les textes légaux applicables.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                with st.chat_message("user", avatar="👤"):
                    st.markdown(msg["content"])
            else:
                with st.chat_message("assistant", avatar="⚖️"):
                    st.markdown(msg["content"])

                    # Afficher sources et calcul
                    if msg.get("sources"):
                        with st.expander(f"📚 {len(msg['sources'])} source(s) juridique(s)", expanded=False):
                            for src in msg["sources"]:
                                badge_class = f"badge-{src.get('domaine', 'general')}"
                                st.markdown(f"""
                                <div class="source-card">
                                    <span class="badge-domaine {badge_class}">{src.get('domaine','?').upper()}</span>
                                    <strong>{src.get('citation', src.get('source',''))}</strong>
                                    — Score: {src.get('score', 0):.2f}<br>
                                    <small style="color:#666">{src.get('texte_extrait','')[:150]}...</small>
                                </div>
                                """, unsafe_allow_html=True)

                    if msg.get("calcul"):
                        with st.expander("🧮 Calcul juridique effectué", expanded=True):
                            st.markdown(f"""
                            <div class="calcul-card">
                                <strong>✅ {msg['calcul']}</strong>
                            </div>
                            """, unsafe_allow_html=True)

    # Gestion question rapide depuis sidebar
    question_initiale = ""
    if hasattr(st.session_state, "question_rapide"):
        question_initiale = st.session_state.question_rapide
        del st.session_state.question_rapide

    # Zone de saisie
    question = st.chat_input("Posez votre question juridique...")

    # Traiter question rapide ou saisie
    question_a_traiter = question or question_initiale

    if question_a_traiter:
        # Ajouter message utilisateur
        st.session_state.messages.append({"role": "user", "content": question_a_traiter})
        st.session_state.nb_questions += 1

        with st.chat_message("user", avatar="👤"):
            st.markdown(question_a_traiter)

        # Générer réponse
        with st.chat_message("assistant", avatar="⚖️"):
            with st.spinner("Recherche dans les textes juridiques..."):
                rep = agent.repondre(
                    question_a_traiter,
                    domaine=st.session_state.domaine_filtre,
                )

            # Afficher réponse en streaming simulé
            st.markdown(rep.reponse)

            # Sources
            if rep.sources:
                with st.expander(f"📚 {len(rep.sources)} source(s) juridique(s)", expanded=False):
                    for src in rep.sources:
                        badge_class = f"badge-{src.get('domaine', 'general')}"
                        st.markdown(f"""
                        <div class="source-card">
                            <span class="badge-domaine {badge_class}">{src.get('domaine','?').upper()}</span>
                            <strong>{src.get('citation', '')}</strong>
                            — Score: {src.get('score', 0):.2f}<br>
                            <small style="color:#666">{src.get('texte_extrait','')[:150]}...</small>
                        </div>
                        """, unsafe_allow_html=True)

            # Calcul effectué
            if rep.calcul_effectue:
                with st.expander("🧮 Calcul juridique effectué", expanded=True):
                    st.markdown(f"""
                    <div class="calcul-card">
                        <strong>✅ {rep.calcul_effectue}</strong>
                    </div>
                    """, unsafe_allow_html=True)

            # Infos
            langue_badge = "🇸🇳 Wolof" if getattr(rep, 'langue_originale', 'fr') == 'wolof' else "🇫🇷 Français"
            st.caption(
                f"{langue_badge} · "
                f"Domaine : {rep.domaine_detecte or 'général'} · "
                f"Sources RAG : {len(rep.sources)} · "
                f"Modèle : {rep.modele} · "
                f"{datetime.now().strftime('%H:%M')}"
            )

        # Sauvegarder dans historique
        st.session_state.messages.append({
            "role": "assistant",
            "content": rep.reponse,
            "sources": rep.sources,
            "calcul": rep.calcul_effectue,
        })

        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# Onglet 2 : Calculateur juridique
# ─────────────────────────────────────────────────────────────────────────────

with tab_calcul:
    st.markdown("### 🧮 Calculateur juridique sénégalais")
    st.markdown("Calculs automatiques basés sur le Code du Travail et les actes OHADA.")

    from src.tools.calcul_juridique import (
        calculer_indemnite_licenciement,
        calculer_preavis,
        calculer_cout_creation_entreprise,
        calculer_prescription,
    )

    calc_type = st.selectbox("Type de calcul", [
        "Indemnité de licenciement",
        "Délai de préavis",
        "Coûts création d'entreprise",
        "Délai de prescription",
    ])

    if calc_type == "Indemnité de licenciement":
        st.markdown("*Base légale : Article L60, Loi 97-17 (Code du Travail SN)*")
        col1, col2, col3 = st.columns(3)
        with col1:
            salaire = st.number_input("Salaire mensuel brut (FCFA)", min_value=50_000,
                                       max_value=10_000_000, value=300_000, step=10_000)
        with col2:
            annees = st.number_input("Années d'ancienneté", min_value=0, max_value=50, value=5)
        with col3:
            mois = st.number_input("Mois supplémentaires", min_value=0, max_value=11, value=0)

        if st.button("Calculer l'indemnité", type="primary", use_container_width=True):
            resultat = calculer_indemnite_licenciement(salaire, annees, mois)
            st.success(f"**Résultat : {resultat.resultat_principal}**")
            for detail in resultat.details:
                if detail.strip():
                    st.markdown(f"- {detail}")
            st.caption(f"Base légale : {resultat.base_legale}")
            st.warning(resultat.avertissement)

    elif calc_type == "Délai de préavis":
        st.markdown("*Base légale : Article L53, Code du Travail SN*")
        col1, col2 = st.columns(2)
        with col1:
            annees_p = st.number_input("Ancienneté (années)", min_value=0, max_value=50, value=3)
        with col2:
            type_c = st.selectbox("Type de contrat", ["CDI", "CDD"])

        if st.button("Calculer le préavis", type="primary", use_container_width=True):
            resultat = calculer_preavis(annees_p, type_c.lower())
            st.success(f"**Résultat : {resultat.resultat_principal}**")
            for detail in resultat.details:
                if detail.strip():
                    st.markdown(f"- {detail}")
            st.caption(f"Base légale : {resultat.base_legale}")

    elif calc_type == "Coûts création d'entreprise":
        st.markdown("*Base légale : AUSCGIE OHADA + Code Général des Impôts SN*")
        col1, col2 = st.columns(2)
        with col1:
            type_soc = st.selectbox("Type de société", ["SARL", "SA", "Entreprise individuelle"])
        with col2:
            capital_input = st.number_input("Capital souhaité (FCFA)", min_value=0,
                                             max_value=1_000_000_000, value=1_000_000, step=100_000)

        if st.button("Calculer les coûts", type="primary", use_container_width=True):
            type_key = type_soc.lower().replace(" ", "_")
            resultat = calculer_cout_creation_entreprise(type_key, capital_input)
            st.success(f"**Résultat : {resultat.resultat_principal}**")
            for detail in resultat.details:
                if detail.strip():
                    st.markdown(f"- {detail}")
            st.caption(f"Base légale : {resultat.base_legale}")
            st.warning(resultat.avertissement)

    elif calc_type == "Délai de prescription":
        type_action = st.selectbox("Type d'action", [
            "licenciement_abusif", "salaires_impayes",
            "action_commerciale_ohada", "action_penale_delit",
            "action_penale_crime", "succession",
        ])
        if st.button("Obtenir le délai", type="primary", use_container_width=True):
            resultat = calculer_prescription(type_action)
            st.success(f"**Résultat : {resultat.resultat_principal}**")
            for detail in resultat.details:
                if detail.strip():
                    st.markdown(f"- {detail}")
            st.caption(f"Base légale : {resultat.base_legale}")


# ─────────────────────────────────────────────────────────────────────────────
# Onglet 3 : Documents indexés
# ─────────────────────────────────────────────────────────────────────────────

with tab_docs:
    st.markdown("### 📚 Base documentaire juridique")

    sources_info = [
        {"nom": "OHADA — Actes Uniformes", "domaine": "ohada",
         "contenu": "AUSCGIE, AU-DCG, AUPSRVE, AUDCIF", "statut": "✅"},
        {"nom": "Code du Travail SN (Loi 97-17)", "domaine": "travail",
         "contenu": "Contrats, licenciement, congés, syndicats", "statut": "✅"},
        {"nom": "Code de la Famille SN (Loi 72-61)", "domaine": "famille",
         "contenu": "Mariage, divorce, succession, tutelle", "statut": "✅"},
        {"nom": "Code Pénal SN", "domaine": "penal",
         "contenu": "Infractions, peines, procédure", "statut": "✅"},
        {"nom": "Loi Domaine National (Loi 64-46)", "domaine": "foncier",
         "contenu": "Terres, titres fonciers, domaine national", "statut": "✅"},
        {"nom": "Loi CDP (Loi 2008-12)", "domaine": "donnees",
         "contenu": "Protection données personnelles", "statut": "✅"},
        {"nom": "Jurisprudence locale", "domaine": "general",
         "contenu": "Décisions tribunaux sénégalais", "statut": "🔄 À collecter"},
        {"nom": "Journal Officiel SN", "domaine": "general",
         "contenu": "Lois et décrets récents", "statut": "🔄 En cours"},
    ]

    for src in sources_info:
        badge_class = f"badge-{src['domaine']}"
        col1, col2, col3 = st.columns([3, 4, 1])
        with col1:
            st.markdown(f"**{src['nom']}**")
        with col2:
            st.caption(src["contenu"])
        with col3:
            st.markdown(src["statut"])

    st.divider()
    st.markdown(f"**Base vectorielle** : {statut['rag']['total']} chunks indexés")
    if statut["rag"]["total"] == 0:
        st.info("Pour indexer les documents : `python scripts/03_indexer_chroma.py`")
    else:
        st.success(f"✅ {statut['rag']['total']} chunks disponibles pour la recherche")
