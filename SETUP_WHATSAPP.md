# Guide Setup WhatsApp — LegalMind Sénégal
Durée : ~15 minutes | Coût : 0€ (sandbox Twilio gratuit)

## Étape 1 — Créer un compte Twilio
1. Aller sur **twilio.com/try-twilio**
2. S'inscrire gratuitement (pas de carte bancaire)
3. Vérifier email + numéro de téléphone

## Étape 2 — Récupérer vos credentials
1. Dashboard Twilio : **console.twilio.com**
2. Copier **Account SID** → `TWILIO_ACCOUNT_SID` dans `.env`
3. Copier **Auth Token** → `TWILIO_AUTH_TOKEN` dans `.env`

## Étape 3 — Activer le sandbox WhatsApp
1. Menu gauche → **Messaging > Try it Out > Send a WhatsApp Message**
2. Vous verrez le numéro sandbox : **+1 415 523 8886**
3. Depuis votre WhatsApp, envoyer au **+1 415 523 8886** :
   ```
   join <votre-mot-sandbox>
   ```
   (ex: `join plenty-tiger` — le mot est affiché dans la console Twilio)
4. Vous recevrez : *"You are now connected to the sandbox"* ✅

## Étape 4 — Installer et lancer ngrok
```cmd
# Télécharger : https://ngrok.com/download
# Créer compte gratuit sur ngrok.com pour URL stable

# Configurer le token
ngrok config add-authtoken VOTRE_TOKEN_NGROK

# Dans un terminal séparé (garder ouvert)
ngrok http 8000
```
Copier l'URL affichée, ex : `https://abc123.ngrok-free.app`

## Étape 5 — Configurer le webhook dans Twilio
1. Twilio Console → **Messaging > Try it Out > Send a WhatsApp Message**
2. Section **"Sandbox Settings"**
3. **"When a message comes in"** → coller :
   ```
   https://abc123.ngrok-free.app/webhook/whatsapp
   ```
4. Méthode : **HTTP POST**
5. Cliquer **Save** ✅

## Étape 6 — Mettre à jour .env
Ajouter dans votre fichier `.env` :
```
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

## Étape 7 — Lancer LegalMind WhatsApp
```cmd
pip install twilio
python whatsapp_webhook.py
```
Vous devriez voir :
```
✅ Twilio configuré
Webhook URL locale : http://localhost:8000/webhook/whatsapp
```

## Étape 8 — Tester sur WhatsApp !
Envoyer au numéro sandbox Twilio :
- `aide` → menu principal
- `Comment créer une SARL ?` → réponse juridique
- `Indemnité 8 ans 300000 FCFA` → calcul automatique
- `wolof` → activer mode wolof 🇸🇳

## Test sans WhatsApp (vérification rapide)
Ouvrir dans le navigateur :
```
http://localhost:8000/health
http://localhost:8000/test?message=Comment+créer+une+SARL
```

## Dépannage
| Problème | Solution |
|----------|---------|
| "Not connected to sandbox" | Renvoyer `join xxx` sur WhatsApp |
| "Webhook not reachable" | Vérifier que ngrok est lancé |
| "Auth error" | Vérifier les credentials dans .env |
| Messages non reçus | Vérifier http://localhost:8000/health |
