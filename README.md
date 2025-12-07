# 🤖 FREYA - Personal AI Agent Assistant

FREYA est un assistant IA personnel qui gère vos fichiers, modifie votre code et exécute des tâches système via des commandes en langage naturel.

**Outils disponibles:** 20 outils intégrés (fichiers, Git, web, système, impression, recherche)
**API:** Groq (gpt-oss-120b)
**Validateur local:** TRM (DeepSeek R1 1.5B) - Valide les actions avant exécution
**Optimisé pour:** Clé API gratuite (8000 TPM)

## 📋 Table des matières

- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Commandes disponibles](#commandes-disponibles)
  - [Gestion de fichiers](#gestion-de-fichiers)
  - [Web](#web)
  - [Opérations Git](#opérations-git)
  - [Système](#système)
  - [Impression](#impression)
- [Architecture](#architecture)
- [TRM Validator](#trm-validator)
- [Optimisation des tokens](#optimisation-des-tokens)

---

## 🚀 Installation

### Prérequis

- Python 3.8+
- Git (pour les fonctionnalités Git)
- Un compte Groq avec une clé API
- **Windows:** pywin32 sera installé automatiquement (pour l'impression)
- **Web scraping:** trafilatura, requests et beautifulsoup4 seront installés automatiquement

### Étapes d'installation

1. **Cloner le projet**
```bash
git clone https://github.com/michel97400/Freya_personal_agent.git
cd Freya_personal_agent
```

2. **Créer un environnement virtuel**
```bash
python -m venv .venv
```

3. **Activer l'environnement virtuel**

**Windows:**
```bash
.\.venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

4. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuration

### Fichier `.env`

FREYA utilise les variables d'environnement pour la configuration. Créez un fichier `.env` à la racine du projet :

```env
GROQ_API_KEY=your_api_key_here
GROQ_API_URL=https://api.groq.com/openai/v1
```

#### Où trouver votre clé API Groq ?

1. Allez sur [console.groq.com](https://console.groq.com)
2. Connectez-vous à votre compte Groq
3. Naviguez vers **API Keys**
4. Créez une nouvelle clé API ou copiez une clé existante
5. Collez-la dans le fichier `.env`

#### Limites de la clé API gratuite

- **8000 tokens par minute (TPM)** - Limite de débit
- **600 requêtes par jour** - Limite quotidienne
- Gratuit jusqu'à ces limites

**⚠️ Important:** 
- Ne commettez **JAMAIS** votre `.env` sur Git (il est déjà dans `.gitignore`)
- Gardez votre clé API privée et sécurisée
- Si vous la compromettez, régénérez-la immédiatement sur console.groq.com

---

## 💬 Utilisation

### Lancer FREYA

```bash
python main.py
```

Vous verrez un message de bienvenue :
```
Bienvenue dans FREYA ! 🤖
Tapez 'exit' ou 'quit' pour arrêter.
```

### Exemple d'interaction

```
>>> Crée un fichier test.txt avec le contenu "Hello World"
✅ Fichier 'test.txt' créé avec succès.

>>> Liste les fichiers du projet
📁 Fichiers du projet:
- agent.py
- main.py
- tools.py
- test.txt

>>> Modifie test.txt et remplace "Hello" par "Bonjour"
✅ 'test.txt' modifié avec succès.

>>> Quitter
Au revoir ! 👋
```

---

## 📚 Commandes disponibles

### 🗂️ Gestion de fichiers

#### `list_files`
Liste tous les fichiers d'un dossier (par défaut le dossier courant)

**Exemples:**
- "Liste les fichiers du projet"
- "Quels fichiers y a-t-il dans le dossier src?"
- "Affiche le contenu du répertoire"

---

#### `read_file`
Lit et affiche le contenu d'un fichier

**Exemples:**
- "Lis le fichier agent.py"
- "Montre-moi le contenu de config.json"
- "Affiche main.py"

---

#### `write_file`
Crée un nouveau fichier avec le contenu spécifié (écrase le fichier s'il existe)

**Exemples:**
- "Crée un fichier app.py avec le code: print('Hello')"
- "Écris un fichier data.json contenant: {...}"
- "Génère un fichier config.ini"

---

#### `modify_file`
Modifie un fichier existant (remplace, insère avant/après, ou ajoute)

**Options d'action:**
- `replace` - Remplace du texte (par défaut)
- `insert_before` - Insère du texte avant
- `insert_after` - Insère du texte après
- `append` - Ajoute du texte à la fin

**Exemples:**
- "Modifie main.py : remplace 'print(a)' par 'print(b)'"
- "Rajoute 'import os' au début de agent.py"
- "Insère 'def nouvelle_fonction():' avant 'def ancienne()'"
- "Ajoute une ligne 'EOF' à la fin de test.txt"

---

#### `delete_path`
Supprime un fichier ou un dossier (récursivement)

**Exemples:**
- "Supprime le fichier test.txt"
- "Efface le dossier __pycache__"
- "Supprime le répertoire temp et tout son contenu"

---

#### `create_folder`
Crée un nouveau dossier

**Exemples:**
- "Crée un dossier nommé src"
- "Crée le dossier data/backup"
- "Crée le répertoire config"

---

#### `search_files`
Recherche un mot ou une expression dans tous les fichiers (par défaut le dossier C:\ sur Windows)

**Exemples:**
- "Recherche 'def calculate' dans le projet"
- "Cherche 'TODO' dans les fichiers Python"
- "Trouve toutes les occurrences de 'import os' dans src/"

---

### 🌐 Web

#### `open_browser`
Ouvre une URL dans le navigateur par défaut ou lance une recherche YouTube

**Exemples:**
- "Ouvre google.com"
- "Va sur github.com"
- "Recherche 'Python tutorial' sur YouTube"
- "Cherche 'musique relaxante' sur YouTube"

---

#### `search_web`
Recherche sur le web via DuckDuckGo et retourne les résultats avec URLs et descriptions

**Paramètres:**
- `query` - Terme de recherche (obligatoire)
- `num_results` - Nombre de résultats (1-10, défaut 5)

**Exemples:**
- "Recherche 'Python web framework'"
- "Cherche 'best practices Node.js'"
- "Trouve les 3 meilleurs résultats pour 'machine learning'"

**Fonctionnalités:**
- ✅ Utilise DuckDuckGo (plus permissif que Google, pas de blocage)
- ✅ Retourne titre, URL, et description pour chaque résultat
- ✅ Pas de clé API requise

---

#### `fetch_webpage`
Récupère et extrait le contenu textuel d'une page web (utilise Trafilatura)

**Paramètres:**
- `url` - URL de la page (ex: https://example.com ou example.com)

**Exemples:**
- "Récupère le contenu de github.com"
- "Extrait le texte de https://example.com/article"
- "Lis la page news.ycombinator.com"

**Fonctionnalités:**
- ✅ Extrait uniquement le contenu textuel pertinent
- ✅ Ignore publicités, scripts, CSS
- ✅ Limite à 2000 caractères pour économiser les tokens

---

#### `search_and_summarize`
Recherche sur le web et extrait automatiquement le contenu de la première page trouvée

**Paramètres:**
- `query` - Terme de recherche

**Exemples:**
- "Trouve une explication sur la cryptographie"
- "Cherche un tutoriel Python et résume-le"
- "Trouve les dernières nouvelles sur l'IA"

---

### 🔧 Opérations Git

#### `git_push`
Effectue git add, commit et push (simple, avec option de branche)

**Paramètres:**
- `commit_message` - Message du commit (obligatoire)
- `branch` - Branche cible (optionnel)

**Exemples:**
- "Fais un git push avec le message 'ajout nouvelle fonction'"
- "Push vers la branche develop avec le message 'bug fix'"

---

#### `git_workflow`
Workflow Git complet : add → commit → détecte la branche → checkout main → merge → push

**Paramètres:**
- `commit_message` - Message du commit (obligatoire)

**Workflow détaillé:**
1. ✅ `git add .` - Ajoute tous les changements
2. 💬 `git commit -m <message>` - Crée un commit
3. 🌿 Détecte la branche actuelle
4. 📍 Si pas sur main : `git checkout main`
5. 🔀 `git merge <branche_précédente>` - Merge dans main
6. 🚀 `git push` - Pousse vers le serveur

**Exemples:**
- "Fais un git workflow avec le message 'mise à jour v1.2'"
- "Exécute le workflow git pour 'nouvelles fonctionnalités'"

---

#### `git_create_branch`
Crée une nouvelle branche et la bascule automatiquement

**Paramètres:**
- `branch_name` - Nom de la nouvelle branche (obligatoire)

**Exemples:**
- "Crée une branche 'feature/nouvelle-fonction'"
- "Crée la branche 'bugfix/fix-login'"
- "Crée une branche 'develop'"

---

#### `git_checkout_branch`
Bascule vers une branche existante (vérifie les changements non commitées)

**Paramètres:**
- `branch_name` - Nom de la branche (obligatoire)

**Exemples:**
- "Bascule vers la branche main"
- "Change de branche, va sur develop"
- "Switch vers feature/test"

---

#### `git_list_branches`
Liste toutes les branches du dépôt (locales et distantes)

**Exemples:**
- "Liste les branches disponibles"
- "Affiche toutes les branches"
- "Quelles branches existe?"

---

### 📊 Système

#### `get_pc_config`
Retourne les informations de configuration du PC

**Retourne:**
- Nombre de cores CPU
- Mémoire RAM (total, disponible, pourcentage utilisé)
- Espace disque (total, libre, pourcentage utilisé)

**Exemples:**
- "Quels sont les specs de mon PC?"
- "Affiche la configuration du système"
- "Combien de RAM j'ai?"

---

#### `launch_application`
Lance une application executable

**Exemples:**
- "Lance Notepad"
- "Ouvre notepad.exe"
- "Exécute C:\\Program Files\\app.exe"

---

#### `install_python_package`
Installe un package Python via pip

**Exemples:**
- "Installe requests"
- "Pip install numpy"
- "Installe pandas via pip"

---

### 🖨️ Impression

#### `print_file`
Imprime un fichier sur une imprimante réseau ou locale

**Paramètres:**
- `file_path` - Chemin du fichier (relatif ou absolu)
- `printer_name` - Nom de l'imprimante (optionnel, utilise l'imprimante par défaut)

**Exemples:**
- "Imprime requirements.txt"
- "Imprime le fichier agent.py"
- "Envoie main.py à l'imprimante"
- "Imprime C:\\Users\\Apprenant\\Desktop\\rapport.pdf sur HP_OfficeJet"

**Fonctionnalités:**
- ✅ Accepte les chemins relatifs et absolus
- ✅ Support des imprimantes réseau (HP OfficeJet, etc.)
- ✅ Gère les erreurs gracieusement
- ✅ Supporte Windows, Linux et macOS

---

## 🏗️ Architecture

### Structure du projet

```
Freya_personal_agent/
├── agent.py           # Cœur de l'agent (classe FreyaAgentNL)
├── tools.py           # Implémentation de toutes les fonctions outils
├── trm_validator.py   # Validateur TRM local (DeepSeek R1 1.5B)
├── freya_llm.py       # Client Groq API
├── main.py            # Interface REPL interactive
├── .env               # Variables d'environnement (À CRÉER)
├── .gitignore         # Fichiers à ignorer (inclut .env)
├── README.md          # Ce fichier
└── test/              # Dossier de tests
```

### Fichiers clés

**`agent.py`**
- `FreyaAgentNL` - Classe principale de l'agent
- `respond(message)` - Point d'entrée pour traiter les demandes
- `call_tool()` - Mappe les noms d'outils aux fonctions
- `TOOL_DEFS` - Définitions des outils disponibles

**`tools.py`**
- Toutes les implémentations des fonctions d'outils
- Gestion complète des erreurs
- Validation des entrées

**`freya_llm.py`**
- Client Groq configuré
- Fonction `ask_groq()` pour les appels API

**`trm_validator.py`**
- Validateur local avec DeepSeek R1 1.5B
- `validate_plan()` - Valide un plan d'exécution complet
- `validate_tool_call()` - Valide un appel d'outil individuel
- Protection des chemins système (Windows, Program Files, etc.)

**`main.py`**
- Boucle REPL interactive
- Gestion des commandes `exit`/`quit`
- Gestion des interruptions (Ctrl+C)

---

## 🛡️ TRM Validator

### Qu'est-ce que le TRM ?

Le **TRM (Tiny Recursive Model)** est un validateur local qui utilise **DeepSeek R1 1.5B** pour vérifier et sécuriser les actions avant leur exécution. Il fonctionne comme une couche de sécurité entre Groq et l'exécution des outils.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    WORKFLOW FREYA                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [1] Requête utilisateur                                    │
│       ↓                                                     │
│  [2] Groq GPT-OSS 120B → génère un PLAN JSON               │
│       ↓                                                     │
│  [3] TRM DeepSeek R1 1.5B → valide/corrige le PLAN         │
│       │                                                     │
│       ├── ✅ Plan approuvé → Exécution                     │
│       ├── ⚠️ Plan corrigé → Exécution du plan corrigé      │
│       └── ❌ Plan rejeté → Message d'erreur                │
│       ↓                                                     │
│  [4] Exécution étape par étape (tools.py)                  │
│       ↓                                                     │
│  [5] Résultat formaté                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Protections actives

| Type | Détails |
|------|---------|
| 🚫 **Chemins système** | `C:\Windows`, `C:\Program Files`, `C:\System32` |
| 🚫 **Racines** | `C:\`, `D:\`, `/`, `\` |
| ⚠️ **Warnings** | Push sur main, suppressions de dossiers |
| ✅ **Arguments** | Vérification des arguments requis |

### Configuration du modèle TRM

Le TRM utilise un modèle GGUF local. Pour l'activer :

1. **Télécharger le modèle** (~1.6GB)
   - Aller sur [HuggingFace - DeepSeek R1 Distill Qwen 1.5B GGUF](https://huggingface.co/lmstudio-community/DeepSeek-R1-Distill-Qwen-1.5B-GGUF)
   - Télécharger `DeepSeek-R1-Distill-Qwen-1.5B-Q8_0.gguf` (version Q8 recommandée)
   - Placer le fichier `.gguf` à la racine du projet

2. **Le validateur se charge automatiquement au démarrage**
```
🧠 Chargement du TRM (DeepSeek R1 1.5B)...
✅ TRM chargé avec succès
```

### Mode dégradé

Si le modèle GGUF n'est pas présent, le TRM fonctionne en **mode règles uniquement** (plus rapide, mais moins intelligent) :
- Validation des chemins dangereux ✅
- Vérification des arguments requis ✅
- Pas d'analyse sémantique des requêtes ❌

---

## 🎯 Optimisation des tokens

FREYA est optimisé pour la clé API Groq gratuite (8000 TPM) avec les stratégies suivantes :

### Limitations de conception

1. **Fenêtre de mémoire réduite** (5 messages max)
   - Réduit la taille des contextes envoyés à l'API
   - Les anciens messages sont automatiquement supprimés

2. **Un seul appel outil par requête**
   - Évite les boucles de continuation qui consomment des tokens
   - Plus rapide et plus économe

3. **Planification désactivée**
   - La création de plans a été désactivée
   - Elle consommait 2-3x plus de tokens

4. **Prompts simplifiés**
   - Système prompt réduit de 80%
   - Instructions directes et concises

### Estimations de consommation

| Action | Tokens estimés |
|--------|---|
| Lister des fichiers | 300-500 |
| Créer/modifier un fichier | 500-800 |
| Opération Git simple | 400-600 |
| Recherche de fichiers | 600-1000 |

**Conseil:** Avec la limite de 8000 TPM, vous pouvez faire environ 10-15 opérations par minute.

---

## 🐛 Dépannage

### "GROQ_API_KEY not found"
- Vérifiez que le fichier `.env` existe à la racine du projet
- Assurez-vous que `GROQ_API_KEY=votre_clé` est correctement écrit
- Redémarrez l'application après modification du `.env`

### "Git n'est pas installé"
- Installez Git depuis [git-scm.com](https://git-scm.com)
- Sur Windows : téléchargez l'installateur et suivez les étapes
- Redémarrez votre terminal après installation

### "Branche n'existe pas"
- Utilisez `git_list_branches` pour voir les branches disponibles
- Vérifiez que vous avez synchronisé avec le serveur distant

### "Dépassement du limite de tokens"
- Réduisez le nombre de requêtes
- Utiliser des commandes plus spécifiques
- Attendez avant la prochaine minute pour réinitialiser le compteur

---

## 📝 Exemples d'utilisation avancée

### Workflow complet : Créer une nouvelle feature

```
>>> Crée une branche feature/ma-fonctionnalite
✅ Branche 'feature/ma-fonctionnalite' créée et activée.

>>> Crée un fichier src/nouvelle_fonction.py avec le code def ma_fonction(): return "Hello"
✅ Fichier créé avec succès.

>>> Modifie src/nouvelle_fonction.py et ajoute un print
✅ Fichier modifié avec succès.

>>> Fais un git workflow avec le message "ajout nouvelle fonction"
✅ Workflow git complété avec succès!
📝 Commit: ajout nouvelle fonction
🌿 Branche: feature/ma-fonctionnalite -> main
```

### Workflow : Chercher et remplacer du code

```
>>> Recherche "TODO" dans le projet
📊 Résultats: 2 occurrences trouvées

>>> Lis agent.py et montre-moi la fonction respond
[contenu affiché]

>>> Modifie agent.py et remplace "TODO" par "DONE"
✅ Fichier modifié avec succès.
```

---

## 🔮 Prochaines améliorations prévues

- [x] TRM Validator local (DeepSeek R1 1.5B)
- [x] Planification avec validation avant exécution
- [ ] Support GPU pour TRM (CUDA)
- [ ] Support de Ollama pour les modèles locaux
- [ ] Déploiement sur RTX 5080/5090
- [ ] Opérations Git avancées (cherry-pick, rebase, stash)
- [ ] Support des webhooks et automations
- [ ] Interface Web (au lieu de REPL)

---

## 📄 Licence

Ce projet est open source. Consultez le fichier LICENSE pour plus de détails.

---

## 👨‍💻 Contributeur

**Michel** - [github.com/michel97400](https://github.com/michel97400)

---

## 💡 Questions ?

Si vous avez des questions, ouvrez une [Issue](https://github.com/michel97400/Freya_personal_agent/issues) sur GitHub.

---

**Dernière mise à jour:** Décembre 2025
