from groq import Groq
import os
from pathlib import Path
from dotenv import load_dotenv

# Charger le .env depuis le dossier du script
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Initialiser le client Groq
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY non définie dans les variables d'environnement")

try:
    # Initialiser le client Groq avec gestion des erreurs
    client = Groq(api_key=api_key)
except TypeError as e:
    # Problème de compatibilité entre groq et httpx
    if "proxies" in str(e):
        # Essayer sans les paramètres problématiques
        import warnings
        warnings.warn(f"Avertissement: Problème de compatibilité détecté. Tentative d'initialisation alternative.")
        # Réinstaller les bonnes versions de dépendances
        print("❌ Erreur de compatibilité détectée.")
        print("Veuillez exécuter: pip install --upgrade groq httpx")
        raise
    else:
        raise

def ask_groq(prompt, history=None):
    """Envoie une requête au modèle Groq avec historique optionnel."""
    if not prompt:
        return "Erreur: le prompt ne peut pas être vide."
    
    messages = []
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": prompt})
    
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages
        )
        return response.choices[0].message.content or "Aucune réponse du modèle."
    except Exception as e:
        return f"Erreur lors de l'appel à Groq: {e}"

