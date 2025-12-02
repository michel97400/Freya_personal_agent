# agent.py
import json
from tools import list_files, read_file, write_file, delete_path, search_files, create_folder, open_browser, modify_file, git_push, git_workflow, git_create_branch, git_checkout_branch, git_list_branches, get_pc_config, install_python_package
from freya_llm import client  # ton client Groq déjà configuré
import os

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
    }

]

def call_tool(tool_name, arguments):
    if tool_name == "list_files":
        path = os.path.abspath(arguments.get("path") or ".")
        return "\n".join(list_files(path))
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
    return "Outil inconnu"


# Agent FREYA en langage naturel
class FreyaAgentNL:
    def __init__(self):
        self.memory = []
        self.max_memory_length = 5  # Réduire à 5 messages pour économiser les tokens

    def _cleanup_memory(self):
        """Nettoie la mémoire si elle dépasse la limite."""
        if len(self.memory) > self.max_memory_length:
            # Garder seulement les derniers messages
            self.memory = self.memory[-self.max_memory_length:]

    def _create_plan(self, message):
        """Crée un plan d'exécution détaillé avant d'agir."""
        planning_prompt = f"""Analyse cette demande et crée un plan d'exécution DÉTAILLÉ:
"{message}"

Réponds avec un plan structuré incluant:
1. Les dossiers à créer (avec chemins complets)
2. Les fichiers à créer (avec chemin et contenu)
3. Les fichiers à modifier
4. L'ordre exact d'exécution

Sois TRÈS PRÉCIS et EXHAUSTIF. Énumère CHAQUE action."""
        
        try:
            planning_response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[{"role": "system", "content": planning_prompt}],
                max_tokens=2000
            )
            plan = planning_response.choices[0].message.content
            return plan
        except Exception as e:
            return f"Plan: Exécuter la demande directement"

    def respond(self, message):
        # Ajouter le message utilisateur à la mémoire
        self.memory.append({"role": "user", "content": message})
        
        # Nettoyer la mémoire si elle est trop grosse
        self._cleanup_memory()
        
        # Déterminer le tool_choice en fonction de la demande
        keywords_require_tools = ["modifi", "rajoute", "ajoute", "change", "remplace", "crée", "écris", "insère", "supprima", "dele", "instal", "pip"]
        requires_tool = any(keyword in message.lower() for keyword in keywords_require_tools)
        
        # Créer un plan si c'est une demande complexe (DÉSACTIVÉ pour économiser tokens)
        # plan = self._create_plan(message) if requires_tool else None
        plan = None
        tool_choice = "required" if requires_tool else "auto"
        
        # Système de prompt simple et optimisé
        system_prompt = """Tu es FREYA, un assistant personnel pour gérer des fichiers, du code et Git.

Outils disponibles:
📁 Fichiers: list_files, read_file, write_file, modify_file, delete_path, create_folder, search_files
🌐 Web: open_browser (URLs et recherches YouTube)
🔧 Git: git_push, git_workflow, git_create_branch, git_checkout_branch, git_list_branches
🐍 Python: install_python_package (pip install)
📊 Système: get_pc_config (CPU, RAM, disque)

Instructions:
- Sois efficace et concis
- Exécute exactement ce que l'utilisateur demande
- Utilise les bons outils pour chaque tâche
- Pour les modifications: utilise modify_file avec l'action appropriée (replace, insert_before, insert_after, append)
- Pour Git: préfère git_workflow pour un workflow complet (add → commit → merge → push)
- Affiche toujours les résultats clairement"""
        
        # Ajouter le plan au prompt si disponible
        if plan:
            system_prompt += f"\n\nPlan:\n{plan}"
        
        # Appel au modèle
        messages_to_send = [{"role": "system", "content": system_prompt}] + self.memory
        
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages_to_send,
            tools=TOOL_DEFS,
            tool_choice=tool_choice  # Force l'utilisation des outils si nécessaire
        )

        resp_msg = response.choices[0].message

        # Gestion des tool_calls (une seule itération pour économiser les tokens)
        if hasattr(resp_msg, "tool_calls") and resp_msg.tool_calls:
            # Ajouter la réponse du modèle avec les tool_calls
            self.memory.append(resp_msg)
            
            # Exécuter tous les outils
            for call in resp_msg.tool_calls:
                fn_name = call.function.name
                args = json.loads(call.function.arguments)
                result = call_tool(fn_name, args)
                
                # Ajouter le résultat de l'outil à la mémoire
                self.memory.append({
                    "role": "tool",
                    "name": fn_name,
                    "content": result,
                    "tool_call_id": call.id
                })

            # Relancer UNE SEULE FOIS le modèle pour la réponse finale
            final_resp = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=messages_to_send + self.memory,
                tools=TOOL_DEFS,
                tool_choice="auto"
            )
            final_content = final_resp.choices[0].message.content or "Tâche complétée."
            self.memory.append({"role": "assistant", "content": final_content})
            return final_content
        else:
            # Pas d'outil appelé, texte direct
            content = resp_msg.content or "Je n'ai pas compris."
            self.memory.append({"role": "assistant", "content": content})
            return content
