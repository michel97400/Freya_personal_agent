# 🔧 Guide de dépannage FREYA

## Erreurs courantes et solutions

### 1. ❌ `TypeError: Client.__init__() got an unexpected keyword argument 'proxies'`

**Cause:** Conflit de compatibilité entre les versions de `groq` et `httpx`.

**Solution:** Réinstallez les dépendances avec les bonnes versions:

```bash
pip install --upgrade groq httpx python-dotenv
```

Ou supprimez et réinstallez complètement:

```bash
pip uninstall groq httpx -y
pip install -r requirements.txt
```

**Détails techniques:**
- Cette erreur survient généralement sous Linux avec Python 3.12+
- Elle est causée par une incompatibilité entre les versions du SDK Groq et de la librairie httpx
- Le fichier `requirements.txt` a été mis à jour pour utiliser des plages de versions compatibles

---

### 2. ❌ `GROQ_API_KEY not found`

**Cause:** Le fichier `.env` manque ou la clé API n'est pas configurée.

**Solution:** 
1. Créez un fichier `.env` à la racine du projet:
```
GROQ_API_KEY=votre_clé_api_ici
```

2. Obtenez votre clé API:
   - Allez sur [console.groq.com](https://console.groq.com)
   - Connectez-vous à votre compte
   - Naviguez vers **API Keys**
   - Copiez votre clé API

3. Redémarrez FREYA

⚠️ **Important:** Ne commitez jamais le `.env` sur Git (il est dans `.gitignore`)

---

### 3. ❌ `ModuleNotFoundError: No module named 'groq'`

**Cause:** Les dépendances ne sont pas installées.

**Solution:**
```bash
pip install -r requirements.txt
```

---

### 4. ❌ `Git n'est pas installé ou introuvable`

**Cause:** Git n'est pas installé ou pas dans le PATH.

**Solution:**

**Windows:**
- Téléchargez Git depuis [git-scm.com](https://git-scm.com)
- Installez-le avec l'option "Add Git to PATH"
- Redémarrez votre terminal

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install git
```

**macOS:**
```bash
brew install git
```

---

### 5. ⚠️ `Accès refusé lors de la recherche`

**Cause:** Permissions insuffisantes pour accéder à certains répertoires.

**Solution:**
- Exécutez FREYA avec les permissions appropriées
- Ou spécifiez un chemin accessible lors de la recherche

**Exemple:**
```
>>> Recherche 'TODO' dans le dossier ./src
```

---

### 6. ⚠️ `psutil non installé - infos limitées`

**Cause:** `psutil` est optionnel mais recommandé.

**Solution:** Installez-le pour obtenir les infos système complètes:
```bash
pip install psutil
```

---

### 7. ❌ `Erreur: accès refusé à '<fichier>'`

**Cause:** FREYA n'a pas les permissions pour accéder au fichier.

**Solutions:**
- Vérifiez les permissions du fichier:
  
  **Windows:**
  ```bash
  icacls <fichier>
  ```
  
  **Linux/macOS:**
  ```bash
  ls -l <fichier>
  chmod 644 <fichier>  # Pour donner la permission de lecture
  ```

---

### 8. ⚠️ Dépassement de la limite de tokens Groq (8000 TPM)

**Cause:** Trop de requêtes API en peu de temps.

**Solutions:**
- Réduisez le nombre de requêtes
- Utilisez des commandes plus spécifiques
- Attendez avant la prochaine minute pour réinitialiser le compteur
- Mettez à niveau votre plan Groq si nécessaire

---

## 📝 Diagnostic

### Vérifier les versions installées:

```bash
pip list | grep -E "groq|httpx|python-dotenv|psutil"
```

Vous devriez voir quelque chose comme:
```
groq               0.10.0
httpx              0.24.0
python-dotenv      1.0.0
psutil             6.0.0
```

### Vérifier la clé API:

```python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
print("✅ Clé trouvée!" if api_key else "❌ Clé manquante!")
```

### Tester la connexion Groq:

```python
from freya_llm import client

try:
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": "Bonjour"}]
    )
    print("✅ Connexion Groq OK!")
    print(response.choices[0].message.content)
except Exception as e:
    print(f"❌ Erreur: {e}")
```

---

## 🐛 Signaler un bug

Si vous rencontrez un problème non listé ici:

1. Notez les étapes pour reproduire le bug
2. Notez le message d'erreur complet
3. Notez votre OS (Windows/Linux/macOS) et version Python
4. Ouvrez une [Issue sur GitHub](https://github.com/michel97400/Freya_personal_agent/issues)

---

## ✅ Checklist de configuration

- [ ] Python 3.8+ installé
- [ ] `.venv` créé et activé
- [ ] `pip install -r requirements.txt` exécuté
- [ ] `.env` créé avec `GROQ_API_KEY`
- [ ] Git installé (pour les fonctionnalités Git)
- [ ] `python main.py` lance FREYA sans erreur

---

## 📞 Support

Pour plus d'aide:
- Consultez le [README.md](README.md)
- Vérifiez la [documentation Groq](https://console.groq.com/docs)
- Ouvrez une Issue sur GitHub

**Dernière mise à jour:** Décembre 2025
