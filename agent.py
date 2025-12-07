# agent.py
import json
from tools import list_files, read_file, write_file, delete_path, search_files, create_folder, open_browser, modify_file, git_push, git_workflow, git_create_branch, git_checkout_branch, git_list_branches, get_pc_config, install_python_package, git_clone, launch_application, print_file, search_web, fetch_webpage, search_and_summarize
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
        # Ne pas inclure "dossier" ou "fichier" ici car ce sont des termes génériques
        context_keywords = ["desktop", "bureau", "documents", "downloads", "téléchargements", "c:\\", "d:\\", "en cours", "actuel", "courant", "ici"]
        has_specific_context = any(ctx in message_lower for ctx in context_keywords)
        
        if has_specific_context:
            requires_tool = True
        
        # Créer un plan si c'est une demande complexe (DÉSACTIVÉ pour économiser tokens)
        # plan = self._create_plan(message) if requires_tool else None
        plan = None
        
        # Détection de demandes vagues (sans contexte spécifique)
        vague_requests = ["liste", "lister", "affiche", "montre", "contenu"]
        is_vague = any(kw in message_lower for kw in vague_requests) and not has_specific_context
        
        # Utiliser "auto" pour : Git, recherche web, et demandes vagues (pour permettre au modèle de demander des précisions)
        if any(kw in message_lower for kw in ["push", "commit", "git", "dépôt", "repo", "recherche", "cherche", "google", "web", "internet"]) or is_vague:
            tool_choice = "auto"
        else:
            tool_choice = "required" if requires_tool else "auto"
        
        # Système de prompt compact pour économiser les tokens
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
