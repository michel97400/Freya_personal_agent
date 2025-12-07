# agent.py
import json
from tools import list_files, read_file, write_file, delete_path, search_files, create_folder, open_browser, modify_file, git_push, git_workflow, git_create_branch, git_checkout_branch, git_list_branches, get_pc_config, install_python_package, git_clone, launch_application, print_file, search_web, fetch_webpage, search_and_summarize
from freya_llm import client  # ton client Groq déjà configuré
from trm_validator import get_validator, validate_tool_call
import os
import re

# Définition des outils pour Groq
TOOL_DEFS = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "Liste les fichiers du projet",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Dossier à lister (optionnel)"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_folder",
            "description": "Crée un dossier à l'emplacement indiqué",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Chemin du dossier à créer"}
                },
                "required": ["path"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Lit un fichier et renvoie son contenu",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Fichier à lire"}
                },
                "required": ["filename"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Écrit dans un fichier",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string"},
                    "content": {"type": "string"}
                },
                "required": ["filename", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "modify_file",
            "description": "Modifie un fichier existant en remplaçant, insérant ou ajoutant du texte",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Fichier à modifier"},
                    "search_text": {"type": "string", "description": "Texte à chercher ou point d'insertion"},
                    "replacement_text": {"type": "string", "description": "Nouveau texte ou texte à insérer"},
                    "action": {"type": "string", "enum": ["replace", "insert_before", "insert_after", "append"], "description": "Action à effectuer (défaut: replace)"}
                },
                "required": ["filename", "search_text", "replacement_text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_path",
            "description": "Supprime un fichier ou un dossier",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Chemin du fichier ou du dossier à supprimer"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_files",
            "description": "Recherche un mot ou une expression dans tous les fichiers d'un dossier et ses sous-dossiers",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Mot ou expression à rechercher"},
                    "path": {"type": "string", "description": "Dossier dans lequel chercher (par défaut le dossier courant)"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_browser",
            "description": "Ouvre une URL ou une recherche YouTube dans le navigateur par défaut",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL à ouvrir (ex: youtube.com, google.com)"},
                    "youtube_search": {"type": "string", "description": "Recherche YouTube (ex: 'musique relaxante')"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_push",
            "description": "Effectue git add, commit et push",
            "parameters": {
                "type": "object",
                "properties": {
                    "commit_message": {"type": "string", "description": "Message du commit"},
                    "branch": {"type": "string", "description": "Branche cible (optionnel)"}
                },
                "required": ["commit_message"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_workflow",
            "description": "Workflow Git complet: add, commit, checkout main, merge et push",
            "parameters": {
                "type": "object",
                "properties": {
                    "commit_message": {"type": "string", "description": "Message du commit"}
                },
                "required": ["commit_message"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_pc_config",
            "description": "Retourne les infos de configuration du PC (CPU, RAM, disque)",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_create_branch",
            "description": "Crée une nouvelle branche Git et la bascule",
            "parameters": {
                "type": "object",
                "properties": {
                    "branch_name": {"type": "string", "description": "Nom de la nouvelle branche"}
                },
                "required": ["branch_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_checkout_branch",
            "description": "Bascule vers une branche Git existante",
            "parameters": {
                "type": "object",
                "properties": {
                    "branch_name": {"type": "string", "description": "Nom de la branche"}
                },
                "required": ["branch_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_list_branches",
            "description": "Liste toutes les branches disponibles du dépôt",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "install_python_package",
            "description": "Installe un paquet Python via pip",
            "parameters": {
                "type": "object",
                "properties": {
                    "package_name": {"type": "string", "description": "Nom du paquet à installer (ex: 'requests', 'numpy==1.21.0')"}
                },
                "required": ["package_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_clone",
            "description": "Clone un dépôt Git à partir d'une URL",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo_url": {"type": "string", "description": "URL du dépôt Git (ex: https://github.com/user/repo.git)"},
                    "target_path": {"type": "string", "description": "Chemin où cloner (optionnel)"}
                },
                "required": ["repo_url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "launch_application",
            "description": "Lance une application (exe, script, etc.)",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_path": {"type": "string", "description": "Chemin complet de l'application (ex: notepad.exe, C:\\\\Program Files\\\\app.exe)"},
                    "arguments": {"type": "string", "description": "Arguments à passer à l'application (optionnel, ex: 'file.txt')"}
                },
                "required": ["app_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "print_file",
            "description": "Imprime un fichier sur une imprimante réseau ou locale",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Chemin complet du fichier à imprimer"},
                    "printer_name": {"type": "string", "description": "Nom de l'imprimante (optionnel, utilise l'imprimante par défaut sinon)"}
                },
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Recherche sur Google et retourne les résultats avec URLs et descriptions",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Terme de recherche"},
                    "num_results": {"type": "integer", "description": "Nombre de résultats à retourner (1-10, défaut 5)"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_webpage",
            "description": "Récupère et extrait le contenu textuel d'une page web",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL de la page (ex: https://example.com ou example.com)"}
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_and_summarize",
            "description": "Recherche sur le web et extrait le contenu de la première page trouvée",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Terme de recherche"}
                },
                "required": ["query"]
            }
        }
    }

]

def call_tool(tool_name, arguments):
    if tool_name == "list_files":
        path = arguments.get("path") or "."
        return list_files(path)
    elif tool_name == "read_file":
        return read_file(arguments["filename"])
    elif tool_name == "write_file":
        filename = arguments["filename"]
        content = arguments["content"]
        return write_file(filename, content)
    elif tool_name == "modify_file":
        filename = arguments["filename"]
        search_text = arguments["search_text"]
        replacement_text = arguments["replacement_text"]
        action = arguments.get("action", "replace")
        return modify_file(filename, search_text, replacement_text, action)
    elif tool_name == "delete_path":
        return delete_path(arguments["path"])
    elif tool_name == "search_files":
        path = arguments.get("path", ".")  # dossier par défaut si non fourni
        query = arguments["query"]         # query est obligatoire
        return search_files(query, path)
    elif tool_name == "create_folder":
        return create_folder(arguments["path"])
    elif tool_name == "open_browser":
        url = arguments.get("url")
        youtube_search = arguments.get("youtube_search")
        return open_browser(url, youtube_search)
    elif tool_name == "git_push":
        commit_message = arguments.get("commit_message", "Automated commit")
        branch = arguments.get("branch")
        return git_push(commit_message, branch)
    elif tool_name == "git_workflow":
        commit_message = arguments.get("commit_message", "Automated commit")
        return git_workflow(commit_message)
    elif tool_name == "get_pc_config":
        config = get_pc_config()
        return str(config)
    elif tool_name == "git_create_branch":
        branch_name = arguments["branch_name"]
        return git_create_branch(branch_name)
    elif tool_name == "git_checkout_branch":
        branch_name = arguments["branch_name"]
        return git_checkout_branch(branch_name)
    elif tool_name == "git_list_branches":
        return git_list_branches()
    elif tool_name == "install_python_package":
        package_name = arguments["package_name"]
        return install_python_package(package_name)
    elif tool_name == "git_clone":
        repo_url = arguments["repo_url"]
        target_path = arguments.get("target_path")
        return git_clone(repo_url, target_path)
    elif tool_name == "launch_application":
        app_path = arguments["app_path"]
        arguments_str = arguments.get("arguments")
        return launch_application(app_path, arguments_str)
    elif tool_name == "print_file":
        file_path = arguments["file_path"]
        printer_name = arguments.get("printer_name")
        return print_file(file_path, printer_name)
    elif tool_name == "search_web":
        query = arguments["query"]
        num_results = arguments.get("num_results", 5)
        return search_web(query, num_results)
    elif tool_name == "fetch_webpage":
        url = arguments["url"]
        return fetch_webpage(url)
    elif tool_name == "search_and_summarize":
        query = arguments["query"]
        return search_and_summarize(query)
    return "Outil inconnu"


# Agent FREYA en langage naturel
class FreyaAgentNL:
    def __init__(self):
        self.memory = []
        self.max_memory_length = 3  # Garder seulement les 3 derniers échanges (6 messages max)

    def _cleanup_memory(self):
        """Nettoie la mémoire de manière agressive pour éviter les dépassements de tokens."""
        # Garder seulement les N derniers échanges (user + assistant)
        if len(self.memory) > self.max_memory_length * 2:
            self.memory = self.memory[-(self.max_memory_length * 2):]
        
        # Si le dernier message est très long (ex: contenu de fichier), le résumer
        for i, msg in enumerate(self.memory):
            # Gérer à la fois les dicts et les objets
            role = msg.get("role") if isinstance(msg, dict) else getattr(msg, "role", None)
            content = msg.get("content", "") if isinstance(msg, dict) else getattr(msg, "content", "")
            
            if role == "assistant" and content and len(content) > 2000:
                if isinstance(msg, dict):
                    msg["content"] = content[:2000] + "\n... [contenu tronqué]"
                else:
                    # Remplacer l'objet par un dict
                    self.memory[i] = {"role": "assistant", "content": content[:2000] + "\n... [contenu tronqué]"}

    def _create_plan(self, message):
        """Crée un plan d'exécution détaillé en JSON avant d'agir."""
        planning_prompt = """Tu es un planificateur d'actions. Analyse la demande et génère un plan JSON.

IMPORTANT: Réponds UNIQUEMENT avec du JSON valide, sans texte avant ou après.

Format requis:
{
  "summary": "Description courte du plan",
  "steps": [
    {"action": "nom_outil", "args": {"arg1": "valeur1"}},
    {"action": "nom_outil2", "args": {"arg2": "valeur2"}}
  ]
}

Outils disponibles:
- list_files: {"path": "chemin"} - Lister fichiers
- read_file: {"filename": "fichier"} - Lire fichier
- write_file: {"filename": "fichier", "content": "contenu"} - CRÉER un NOUVEAU fichier (ÉCRASE si existe!)
- delete_path: {"path": "chemin"} - Supprimer fichier/dossier
- create_folder: {"path": "chemin"} - Créer dossier
- modify_file: {"filename": "fichier", "search_text": "texte_existant", "replacement_text": "nouveau_texte", "action": "replace|insert_after|insert_before|append"} - MODIFIER fichier existant
- search_files: {"pattern": "motif", "path": "chemin"}
- git_workflow: {"message": "commit msg"} - Add, commit, push
- git_push: {} - Push uniquement
- open_browser: {"url": "url"} - Ouvrir navigateur
- search_web: {"query": "recherche"} - Recherche web (retourne liens uniquement)
- fetch_webpage: {"url": "url"} - Récupérer contenu d'une page
- search_and_summarize: {"query": "recherche"} - Recherche + extraction contenu + résumé (pour rapports détaillés)
- launch_application: {"app_name": "nom"} - Lancer application
- print_file: {"file_path": "chemin/fichier"} - Imprimer fichier (file_path OBLIGATOIRE!)

⚠️ RÈGLES CRITIQUES pour les fichiers de CODE:
- Pour AJOUTER une fonction/classe dans un fichier EXISTANT → utilise modify_file avec action="append"
- Pour MODIFIER du code existant → utilise modify_file avec action="replace"
- write_file ÉCRASE TOUT le fichier ! Ne l'utilise QUE pour créer un NOUVEAU fichier
- Pour ajouter du code à la fin: modify_file avec search_text="" et action="append"

Mappings chemins:
- bureau/desktop → C:\\Users\\Payet\\Desktop
- documents → C:\\Users\\Payet\\Documents
- Par défaut (si aucun chemin spécifié) → dossier courant du projet (chemin relatif)

RÈGLES IMPORTANTES:
1. Si l'utilisateur ne précise PAS où créer le fichier, utilise un chemin RELATIF (ex: "output.txt")
2. Si l'utilisateur dit "ça", "le résumé", "le résultat", utilise le CONTEXTE ci-dessous
3. Pour write_file, le "content" est OBLIGATOIRE - utilise le contexte si nécessaire
4. Pour print_file, utilise "file_path" (pas "filename")
"""
        
        # Ajouter le contexte de la conversation (dernier résultat assistant)
        context = ""
        for msg in reversed(self.memory):
            if isinstance(msg, dict) and msg.get("role") == "assistant" and msg.get("content"):
                content = msg["content"]
                if len(content) > 50:  # Ignorer les réponses courtes
                    context = content[:1500]  # Limiter à 1500 chars
                    break
        
        if context:
            planning_prompt += f"\n\nCONTEXTE (résultat précédent à utiliser si l'utilisateur y fait référence):\n{context}\n"
        
        planning_prompt += "\nDemande utilisateur: "
        
        try:
            planning_response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {"role": "system", "content": planning_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=800,
                temperature=0.1
            )
            plan_text = planning_response.choices[0].message.content
            
            # Nettoyer et parser le JSON
            plan_text = plan_text.strip()
            # Enlever les backticks markdown si présents
            if plan_text.startswith("```"):
                plan_text = re.sub(r'^```(?:json)?\n?', '', plan_text)
                plan_text = re.sub(r'\n?```$', '', plan_text)
            
            plan = json.loads(plan_text)
            return plan
            
        except json.JSONDecodeError as e:
            print(f"⚠️ Plan JSON invalide: {e}")
            return None
        except Exception as e:
            print(f"⚠️ Erreur création plan: {e}")
            return None

    def respond(self, message):
        # Ajouter le message utilisateur à la mémoire
        self.memory.append({"role": "user", "content": message})
        
        # Nettoyer la mémoire si elle est trop grosse
        self._cleanup_memory()
        
        # Déterminer le tool_choice en fonction de la demande
        message_lower = message.lower()
        
        # Keywords qui demandent explicitement les outils
        keywords_require_tools = [
            # Modifications
            "modifi", "rajoute", "ajoute", "change", "remplace", "crée", "écris", "insère", "supprim", "supprime", "supprimer", "dele", "delete", "efface",
            # Installation/packages
            "instal", "pip",
            # Git
            "clone", "repo", "dépôt", "push", "commit", "merge", "branch",
            # Actions système
            "lance", "ouvre", "exécute", "app",
            # Impression
            "imprim", "imprimer", "imprime", "print", "printer",
            # Recherche web
            "recherche", "cherche", "google", "web", "internet", "trouve", "chercher", "trouver", "résumé", "article", "page", "site",
            # Listing/affichage - TOUS les termes pour les requêtes de contenu
            "liste", "liste moi", "liste tous",  "lister", "affiche", "afficher", "montre", "montrer", "contenu", "quoi", "quel", "quelle",
            "lis", "voir", "dossier", "fichier", "bureau", "desktop", "élément", "item", "fichiers", "dossiers",
            "répertoire", "arborescence", "structure", "dans", "aller", "qu'il", "éléments"
        ]
        requires_tool = any(keyword in message_lower for keyword in keywords_require_tools)
        
        # Contexte supplémentaire: si mention de chemin SPÉCIFIQUE → force les outils
        context_keywords = ["desktop", "bureau", "documents", "downloads", "téléchargements", "c:\\", "d:\\", "en cours", "actuel", "courant", "ici"]
        has_specific_context = any(ctx in message_lower for ctx in context_keywords)
        
        if has_specific_context:
            requires_tool = True
        
        # ========================================
        # NOUVEAU WORKFLOW AVEC TRM VALIDATION
        # ========================================
        
        # Actions complexes nécessitant planification TRM
        complex_actions = [
            # Création/écriture de fichiers
            "crée", "créer", "créé", "créée", "création",
            "écris", "écrire", "écrit", "écriture",
            "génère", "générer", "génère", "génération",
            "fabrique", "fabriquer", "produis", "produire",
            "fait", "faire", "fais",
            "met", "mettre", "mets",
            "sauvegarde", "sauvegarder", "enregistre", "enregistrer",
            "stocke", "stocker", "conserve", "conserver",
            "copie", "copier", "duplique", "dupliquer",
            "exporte", "exporter",
            
            # Modification de fichiers
            "modifi", "modifier", "modifie",
            "change", "changer", "changes",
            "remplace", "remplacer", "remplacement",
            "rajoute", "rajouter", "ajoute", "ajouter", "ajout",
            "insère", "insérer", "insertion",
            "édite", "éditer", "édition",
            "corrige", "corriger", "correction",
            "update", "upgrade", "maj", "mise à jour",
            "renomme", "renommer", "rename",
            "déplace", "déplacer", "move", "bouge", "bouger",
            
            # Suppression
            "supprim", "supprimer", "supprime", "suppression",
            "delete", "del", "remove",
            "efface", "effacer", "effacement",
            "retire", "retirer", "enlève", "enlever",
            "vide", "vider", "nettoie", "nettoyer", "nettoyage",
            "détruit", "détruire", "destruction",
            
            # Création de dossiers
            "dossier", "répertoire", "directory", "folder",
            "mkdir", "nouveau dossier",
            
            # Git operations
            "git", "push", "commit", "clone", "pull", "fetch",
            "merge", "branch", "checkout", "stash", "rebase",
            "add", "staging", "staged",
            
            # Impression
            "imprim", "imprimer", "imprime", "impression",
            "print", "printer", "imprimante",
            
            # Installation
            "install", "installe", "installer", "installation",
            "pip", "package", "module", "librairie", "bibliothèque",
            "désinstall", "uninstall",
            
            # Lancement/exécution
            "lance", "lancer", "exécute", "exécuter", "run",
            "démarre", "démarrer", "start", "ouvre", "ouvrir",
            
            # Téléchargement
            "télécharge", "télécharger", "download",
            "récupère", "récupérer", "fetch",
            
            # Multi-étapes (plusieurs actions)
            " et ", " puis ", " ensuite ", " après ", " avant ",
            " aussi ", " également ", " en plus ",
            " d'abord ", " finalement ", " enfin "
        ]
        needs_planning = any(kw in message_lower for kw in complex_actions)
        
        if needs_planning and requires_tool:
            return self._execute_with_plan(message, message_lower)
        
        # ========================================
        # WORKFLOW STANDARD (sans planification)
        # ========================================
        
        # Détection de demandes vagues (sans contexte spécifique)
        vague_requests = ["liste", "lister", "affiche", "montre", "contenu"]
        is_vague = any(kw in message_lower for kw in vague_requests) and not has_specific_context
        
        # Utiliser "auto" pour : Git, recherche web, et demandes vagues
        if any(kw in message_lower for kw in ["push", "commit", "git", "dépôt", "repo", "recherche", "cherche", "google", "web", "internet"]) or is_vague:
            tool_choice = "auto"
        else:
            tool_choice = "required" if requires_tool else "auto"
        
        # Système de prompt compact
        system_prompt = """FREYA - Assistant fichiers/code/Git. Accès complet système.

Mappings: bureau→C:\\Users\\Payet\\Desktop, documents→C:\\Users\\Payet\\Documents

Outils: list_files, read_file, write_file, modify_file, delete_path, create_folder, search_files, 
open_browser, search_web, fetch_webpage, search_and_summarize, git_*, install_python_package, 
launch_application, print_file, get_pc_config

Règles:
- "supprime/efface/delete" → utilise delete_path (PAS list_files!)
- "liste/affiche/montre" → utilise list_files
- Exécute les outils et retourne TOUS les résultats
- Formate clairement (emojis, indentation)
- Chemins absolus ou relatifs acceptés
- Git: préfère git_workflow pour workflow complet"""
        
        # Appel au modèle
        messages_to_send = [{"role": "system", "content": system_prompt}] + self.memory
        
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages_to_send,
            tools=TOOL_DEFS,
            tool_choice=tool_choice
        )

        resp_msg = response.choices[0].message
        
        return self._process_response(resp_msg, message, message_lower, messages_to_send, requires_tool)
    
    def _execute_with_plan(self, message, message_lower):
        """Exécute une requête avec planification et validation TRM."""
        print("📋 Création du plan d'exécution...")
        
        # 1. Groq génère un plan JSON
        plan = self._create_plan(message)
        
        if not plan:
            # Fallback: exécution directe sans plan
            print("⚠️ Plan non généré, exécution directe")
            return self._execute_direct(message, message_lower)
        
        print(f"📋 Plan généré: {plan.get('summary', 'N/A')}")
        print(f"   {len(plan.get('steps', []))} étapes")
        
        # 2. TRM valide le plan
        validator = get_validator()
        validation = validator.validate_plan(plan, message)
        
        print(f"🔍 Validation TRM: {validation['feedback'][:100]}...")
        
        # 3. Si plan rejeté ou partiellement rejeté
        if not validation["approved"]:
            # Utiliser le plan corrigé s'il existe
            if validation["corrected_plan"] and validation["corrected_plan"]["steps"]:
                plan = validation["corrected_plan"]
                print(f"🔄 Plan corrigé: {len(plan['steps'])} étapes valides")
            else:
                # Plan entièrement rejeté
                error_msg = f"❌ Plan rejeté par le validateur TRM:\n{validation['feedback']}"
                self.memory.append({"role": "assistant", "content": error_msg})
                return error_msg
        
        # 4. Afficher les warnings
        if validation["warnings"]:
            for warning in validation["warnings"]:
                print(f"   {warning}")
        
        # 5. Exécuter le plan validé
        print("🚀 Exécution du plan validé...")
        return self._execute_plan(plan, message_lower)
    
    def _execute_plan(self, plan, message_lower):
        """Exécute un plan validé étape par étape."""
        all_results = []
        
        for i, step in enumerate(plan.get("steps", [])):
            action = step.get("action", "")
            args = step.get("args", {})
            
            print(f"   [{i+1}] {action}...")
            
            # Dernière validation avant exécution (règles uniquement, rapide)
            validation = validate_tool_call(action, args, "")
            if not validation["approved"]:
                all_results.append(f"❌ Étape {i+1} bloquée: {validation['reason']}")
                continue
            
            # Exécuter l'outil
            try:
                result = call_tool(action, args)
                all_results.append(f"✅ {action}: {result[:500] if len(result) > 500 else result}")
            except Exception as e:
                all_results.append(f"❌ {action}: Erreur - {e}")
        
        # Compiler les résultats
        combined_result = f"📋 **Plan exécuté: {plan.get('summary', 'N/A')}**\n\n"
        combined_result += "\n".join(all_results)
        
        self.memory.append({"role": "assistant", "content": combined_result})
        return combined_result
    
    def _execute_direct(self, message, message_lower):
        """Exécution directe sans planification (fallback)."""
        system_prompt = """FREYA - Assistant fichiers/code/Git. Accès complet système.
Mappings: bureau→C:\\Users\\Payet\\Desktop, documents→C:\\Users\\Payet\\Documents
Exécute directement la demande avec les outils appropriés."""
        
        messages_to_send = [{"role": "system", "content": system_prompt}] + self.memory
        
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages_to_send,
            tools=TOOL_DEFS,
            tool_choice="required"
        )
        
        return self._process_response(response.choices[0].message, message, message_lower, messages_to_send, True)
    
    def _process_response(self, resp_msg, message, message_lower, messages_to_send, requires_tool):

        # Gestion des tool_calls (une seule itération pour économiser les tokens)
        if hasattr(resp_msg, "tool_calls") and resp_msg.tool_calls:
            # Convertir resp_msg en dictionnaire avant de l'ajouter
            msg_dict = {
                "role": "assistant",
                "content": resp_msg.content or "",
                "tool_calls": [{
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments}
                } for tc in resp_msg.tool_calls]
            }
            self.memory.append(msg_dict)
            
            # Exécuter TOUS les outils et collecter les résultats
            all_results = []
            for call in resp_msg.tool_calls:
                fn_name = call.function.name
                args = json.loads(call.function.arguments)
                result = call_tool(fn_name, args)
                all_results.append(result)
                
                # Ajouter le résultat de l'outil à la mémoire
                self.memory.append({
                    "role": "tool",
                    "name": fn_name,
                    "content": result,
                    "tool_call_id": call.id
                })

            # Pour les requêtes de listing/affichage, retourner directement les résultats
            if any(kw in message_lower for kw in ["liste", "lister", "affiche", "afficher", "montre", "montrer", "contenu", "élément", "dossier", "fichier", "bureau", "desktop", "voir", "quel", "quoi"]):
                combined_result = "\n".join(all_results) if all_results else "Aucun résultat."
                self.memory.append({"role": "assistant", "content": combined_result})
                return combined_result
            
            # Pour les impressions, retourner directement le résultat
            if any(kw in message_lower for kw in ["imprim", "imprimer", "imprime", "print", "printer"]):
                combined_result = "\n".join(all_results) if all_results else "Impression complétée."
                self.memory.append({"role": "assistant", "content": combined_result})
                return combined_result
            
            # Pour les recherches web, retourner directement les résultats
            if any(kw in message_lower for kw in ["recherche", "cherche", "google", "web", "internet", "trouve", "chercher", "trouver", "résumé", "article", "page", "site"]):
                combined_result = "\n".join(all_results) if all_results else "Aucun résultat trouvé."
                self.memory.append({"role": "assistant", "content": combined_result})
                return combined_result
            
            # Pour les autres requêtes, demander une réponse au modèle
            final_resp = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=messages_to_send + self.memory,
                tools=TOOL_DEFS,
                tool_choice="auto"
            )
            final_content = final_resp.choices[0].message.content or "Opération complétée."
            self.memory.append({"role": "assistant", "content": final_content})
            return final_content
        else:
            # Pas d'outil appelé - vérifier si on était censé en appeler
            if requires_tool and not (hasattr(resp_msg, "tool_calls") and resp_msg.tool_calls):
                # FALLBACK: Le modèle a ignoré tool_choice="required"
                # Détecter ce qui était demandé et appeler l'outil approprié
                
                # Git push/workflow
                if any(kw in message_lower for kw in ["push", "commit", "git", "dépôt", "repo"]):
                    # Utiliser un message de commit par défaut
                    commit_msg = "Mise à jour du projet"
                    # Chercher un message de commit dans le message original
                    if "message" in message_lower or ":" in message:
                        # Essayer d'extraire un message entre guillemets
                        import re
                        quoted = re.findall(r'["\']([^"\']+)["\']', message)
                        if quoted:
                            commit_msg = quoted[0]
                    result = git_workflow(commit_msg)
                    self.memory.append({
                        "role": "tool",
                        "name": "git_workflow",
                        "content": result,
                        "tool_call_id": "fallback_git_workflow"
                    })
                    self.memory.append({"role": "assistant", "content": result})
                    return result
                
                # Listing/listing
                if any(kw in message_lower for kw in ["liste", "lister", "affiche", "afficher", "montre", "montrer", "contenu", "élément", "dossier", "fichier", "bureau", "desktop"]):
                    # C'était une requête de listing - appeler list_files sur Desktop
                    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
                    result = list_files(desktop_path)
                    self.memory.append({
                        "role": "tool",
                        "name": "list_files",
                        "content": result,
                        "tool_call_id": "fallback_list_files"
                    })
                    # Retourner directement le résultat avec le contenu
                    self.memory.append({"role": "assistant", "content": result})
                    return result
            
            # Pas d'outil appelé, texte direct
            content = resp_msg.content or "Je n'ai pas compris."
            self.memory.append({"role": "assistant", "content": content})
            return content
