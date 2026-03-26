"""
LegalMind Sénégal — WhatsApp Business (Twilio)
Webhook FastAPI complet et testé

SETUP (15 minutes) :
1. Créer compte sur twilio.com (gratuit)
2. Aller dans Messaging > Try it Out > Send a WhatsApp Message
3. Suivre les instructions du sandbox Twilio :
   - Envoyer "join <mot-sandbox>" au +1 415 523 8886
4. Installer ngrok : https://ngrok.com/download
5. Dans un terminal : ngrok http 8000
6. Copier l'URL ngrok (ex: https://abc123.ngrok-free.app)
7. Dans Twilio sandbox settings :
   - "When a message comes in" → https://abc123.ngrok-free.app/webhook/whatsapp
8. Lancer : python whatsapp_webhook.py
9. Envoyer un message WhatsApp au numéro sandbox Twilio !

Variables .env requises :
    TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
"""

import os, sys, hashlib
from datetime import datetime
from loguru import logger
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, Form, Response, Request
from fastapi.responses import PlainTextResponse

# ── Config ──────────────────────────────────────────────────────────────────
TWILIO_SID   = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_FROM  = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
MAX_WA_CHARS = 1500

app = FastAPI(title="LegalMind WhatsApp", version="2.0.0")

# Sessions en mémoire (user_id → state)
sessions: dict[str, dict] = {}
_agent = None

# ── Chargement agent ────────────────────────────────────────────────────────
def get_agent():
    global _agent
    if _agent is None:
        from src.rag.retriever import LegalRetriever
        from src.agent.agent import LegalMindAgent
        _agent = LegalMindAgent(retriever=LegalRetriever())
        logger.info("Agent LegalMind chargé")
    return _agent

# ── Gestion session ─────────────────────────────────────────────────────────
def get_session(phone: str) -> dict:
    uid = hashlib.md5(phone.encode()).hexdigest()[:8]
    if uid not in sessions:
        sessions[uid] = {
            "uid": uid,
            "phone": phone[-6:],
            "messages": 0,
            "langue": "fr",
            "created": datetime.now().isoformat(),
        }
    return sessions[uid]

# ── Formatage WhatsApp ───────────────────────────────────────────────────────
def formater_wa(texte: str, sources=None, calcul=None) -> str:
    import re
    texte = re.sub(r'\*\*(.+?)\*\*', r'*\1*', texte)
    texte = re.sub(r'#{1,3}\s*(.+)', r'📌 *\1*', texte)
    texte = re.sub(r'\n{3,}', '\n\n', texte)

    if calcul:
        texte = f"🧮 _{calcul}_\n\n" + texte

    if sources:
        refs = [s["article"] for s in sources[:2] if s.get("article")]
        if refs:
            texte += f"\n\n📚 {' | '.join(refs)}"

    if len(texte) > MAX_WA_CHARS:
        texte = texte[:MAX_WA_CHARS - 80] + "\n\n_[Réponse raccourcie — visitez notre site pour plus]_"

    texte += "\n\n⚠️ _Info générale — consultez un avocat pour votre cas_"
    return texte

# ── Envoi message Twilio ─────────────────────────────────────────────────────
async def envoyer_wa(destinataire: str, message: str) -> bool:
    if not TWILIO_SID or not TWILIO_TOKEN:
        logger.warning(f"[SIMULATION] → {destinataire[-6:]}: {message[:60]}...")
        return False
    try:
        from twilio.rest import Client
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        msg = client.messages.create(
            body=message, from_=TWILIO_FROM, to=destinataire
        )
        logger.success(f"Twilio SID: {msg.sid}")
        return True
    except ImportError:
        logger.warning("pip install twilio")
        return False
    except Exception as e:
        logger.error(f"Twilio erreur: {e}")
        return False

# ── Messages système ─────────────────────────────────────────────────────────
MSG_AIDE = """⚖️ *LegalMind Sénégal*
_Assistant juridique IA_

*Exemples :*
• Comment créer une SARL ?
• Indemnité licenciement 8 ans 300000 FCFA
• Préavis CDI 5 ans
• Titre foncier vs permis habiter

*Commandes :*
• *aide* — ce menu
• *reset* — effacer l'historique
• *statut* — état du système
• *wolof* — activer le mode wolof 🇸🇳
• *français* — activer le mode français 🇫🇷"""

MSG_BIENVENUE = """🇸🇳 *Bienvenido à LegalMind !*

Je suis votre assistant juridique pour le droit sénégalais et OHADA.

Posez-moi n'importe quelle question juridique.
Tapez *aide* pour voir les exemples."""

# ── Webhook principal ────────────────────────────────────────────────────────
@app.post("/webhook/whatsapp")
async def webhook(
    Body: str = Form(default=""),
    From: str = Form(default=""),
    To:   str = Form(default=""),
    MessageSid: str = Form(default=""),
):
    if not Body or not From:
        return Response(
            '<?xml version="1.0"?><Response></Response>',
            media_type="application/xml"
        )

    logger.info(f"WA [{From[-6:]}]: {Body[:60]}")
    session = get_session(From)
    session["messages"] += 1
    cmd = Body.strip().lower()

    # ── Commandes spéciales ──────────────────────────────────────────────────
    if cmd == "aide":
        reponse = MSG_AIDE

    elif cmd == "reset":
        session["messages"] = 0
        reponse = "✅ Historique effacé. Posez votre question."

    elif cmd == "statut":
        agent = get_agent()
        st = agent.statut()
        reponse = (
            f"⚙️ *Statut LegalMind*\n"
            f"• API LLM : {'✅' if st['api_configuree'] else '⚠️'}\n"
            f"• Chunks RAG : {st['rag']['total']:,}\n"
            f"• Langue : {'🇸🇳 Wolof' if session.get('langue')=='wo' else '🇫🇷 Français'}\n"
            f"• Vos messages : {session['messages']}"
        )

    elif cmd == "wolof":
        session["langue"] = "wo"
        reponse = "🇸🇳 Mode wolof activé ! Écrivez en wolof, je comprends."

    elif cmd == "français" or cmd == "francais":
        session["langue"] = "fr"
        reponse = "🇫🇷 Mode français activé."

    elif session["messages"] == 1:
        # Premier message → accueil
        reponse = MSG_BIENVENUE
        # Traiter quand même la question si c'est pas une commande
        if len(Body) > 5:
            try:
                agent = get_agent()
                rep = agent.repondre(Body)
                reponse = MSG_BIENVENUE + "\n\n---\n\n" + formater_wa(
                    rep.reponse, rep.sources, rep.calcul_effectue
                )
            except Exception:
                pass  # garder le message de bienvenue

    else:
        # ── Question juridique normale ───────────────────────────────────────
        try:
            agent = get_agent()
            rep = agent.repondre(Body)
            reponse = formater_wa(rep.reponse, rep.sources, rep.calcul_effectue)
        except Exception as e:
            logger.error(f"Erreur agent: {e}")
            reponse = "⚠️ Erreur temporaire. Reformulez votre question ou tapez *aide*."

    # ── Envoyer réponse ──────────────────────────────────────────────────────
    await envoyer_wa(From, reponse)

    return Response(
        '<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
        media_type="application/xml",
        status_code=200,
    )

# ── Routes utilitaires ───────────────────────────────────────────────────────
@app.get("/")
async def accueil():
    return {
        "service": "LegalMind Sénégal — WhatsApp API",
        "status": "running",
        "webhook": "POST /webhook/whatsapp",
        "twilio_configure": bool(TWILIO_SID),
        "sessions_actives": len(sessions),
    }

@app.get("/health")
async def health():
    agent = get_agent()
    st = agent.statut()
    return {
        "ok": True,
        "llm": st["api_configuree"],
        "rag_chunks": st["rag"]["total"],
        "sessions": len(sessions),
        "twilio": bool(TWILIO_SID),
    }

@app.get("/test")
async def test_wa(message: str = "Comment créer une SARL ?"):
    """Tester l'agent sans WhatsApp."""
    agent = get_agent()
    rep = agent.repondre(message)
    return {
        "question": message,
        "reponse_wa": formater_wa(rep.reponse, rep.sources, rep.calcul_effectue),
        "domaine": rep.domaine_detecte,
        "sources": len(rep.sources),
    }

# ── Lancement ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    logger.info("="*50)
    logger.info("LegalMind WhatsApp — Démarrage")
    logger.info("="*50)

    if not TWILIO_SID:
        logger.warning("TWILIO_ACCOUNT_SID manquant dans .env")
        logger.warning("L'agent fonctionnera mais ne pourra pas envoyer de messages")
    else:
        logger.success("Twilio configuré ✅")

    logger.info("Webhook URL locale : http://localhost:8000/webhook/whatsapp")
    logger.info("Test API          : http://localhost:8000/test")
    logger.info("")
    logger.info("Pour exposer au web :")
    logger.info("  1. Ouvrir un 2e terminal")
    logger.info("  2. ngrok http 8000")
    logger.info("  3. Copier l'URL https://xxxx.ngrok-free.app")
    logger.info("  4. Twilio Console > Sandbox Settings > When a message comes in")
    logger.info("  5. Coller : https://xxxx.ngrok-free.app/webhook/whatsapp")

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
