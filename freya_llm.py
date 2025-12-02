from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

# Initialiser le client Groq
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY non définie dans les variables d'environnement")

client = Groq(api_key=api_key)

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

