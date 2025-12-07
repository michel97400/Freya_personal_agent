import os
import shutil
import webbrowser
import subprocess
import requests
import trafilatura
from urllib.parse import urljoin

def list_files(path="."):
    """Liste tous les fichiers et dossiers d'un répertoire."""
    try:
        path = os.path.abspath(path)
        items = os.listdir(path)
        
        if not items:
            return f"📁 Le répertoire '{path}' est vide."
        
        # Séparer fichiers et dossiers
        files = []
        folders = []
        
        for item in items:
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                folders.append(item)
            else:
                files.append(item)
        
        result = f"📁 Contenu de '{path}':\n\n"
        
        if folders:
            result += "📂 Dossiers:\n"
            for folder in sorted(folders):
                result += f"  - {folder}/\n"
            result += "\n"
        
        if files:
            result += "📄 Fichiers:\n"
            for file in sorted(files):
                result += f"  - {file}\n"
        
        return result
    except FileNotFoundError:
        return f"❌ Erreur: le chemin '{path}' n'existe pas."
    except PermissionError:
        return f"❌ Erreur: accès refusé à '{path}'."
    except Exception as e:
        return f"❌ Erreur lors de la lecture du répertoire: {e}"

def read_file(path):
    """Lit et retourne le contenu d'un fichier."""
    if not os.path.exists(path):
        return f"Erreur: le fichier '{path}' n'existe pas."
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        return f"Erreur: impossible de lire '{path}' (fichier binaire ou encodage incompatible)."
    except PermissionError:
        return f"Erreur: accès refusé à '{path}'."
    except Exception as e:
        return f"Erreur lors de la lecture: {e}"

def create_folder(path):
    """
    Crée un dossier à l'emplacement indiqué.
    Renvoie un message de confirmation ou d'erreur.
    """
    path = os.path.abspath(path)
    if os.path.exists(path):
        return f"⚠️ Le dossier '{path}' existe déjà."
    try:
        os.makedirs(path)
        return f"✅ Le dossier '{path}' a été créé."
    except Exception as e:
        return f"❌ Impossible de créer le dossier '{path}': {e}"

def write_file(filename, content):
    """Écrit du contenu dans un fichier (crée ou écrase)."""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        return f"✅ Le fichier '{filename}' a été créé/modifié."
    except PermissionError:
        return f"❌ Erreur: accès refusé à '{filename}'."
    except Exception as e:
        return f"❌ Erreur lors de l'écriture: {e}"


def modify_file(filename, search_text, replacement_text, action="replace"):
    """
    Modifie un fichier existant en remplaçant ou insérant du texte.
    
    Actions disponibles:
    - "replace": remplace search_text par replacement_text
    - "insert_before": insère replacement_text avant search_text
    - "insert_after": insère replacement_text après search_text
    - "append": ajoute replacement_text à la fin du fichier
    """
    if not os.path.exists(filename):
        return f"❌ Erreur: le fichier '{filename}' n'existe pas."
    
    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
        
        if action == "replace":
            if search_text not in content:
                return f"⚠️ Le texte à remplacer n'a pas été trouvé dans '{filename}'."
            new_content = content.replace(search_text, replacement_text)
        
        elif action == "insert_before":
            if search_text not in content:
                return f"⚠️ Le point d'insertion n'a pas été trouvé dans '{filename}'."
            new_content = content.replace(search_text, replacement_text + search_text)
        
        elif action == "insert_after":
            if search_text not in content:
                return f"⚠️ Le point d'insertion n'a pas été trouvé dans '{filename}'."
            new_content = content.replace(search_text, search_text + replacement_text)
        
        elif action == "append":
            new_content = content + "\n" + replacement_text if content else replacement_text
        
        else:
            return f"❌ Action inconnue: '{action}'. Utilisez 'replace', 'insert_before', 'insert_after' ou 'append'."
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(new_content)
        
        return f"✅ Le fichier '{filename}' a été modifié avec succès."
    
    except PermissionError:
        return f"❌ Erreur: accès refusé à '{filename}'."
    except Exception as e:
        return f"❌ Erreur lors de la modification: {e}"


def delete_path(path):
    """
    Supprime le fichier ou le dossier indiqué.
    Retourne un message de confirmation ou d'erreur.
    """
    if not os.path.exists(path):
        return f"⚠️ Le chemin '{path}' n'existe pas."

    try:
        if os.path.isfile(path):
            os.remove(path)
            return f"✅ Le fichier '{path}' a été supprimé."
        elif os.path.isdir(path):
            shutil.rmtree(path)
            return f"✅ Le dossier '{path}' et son contenu ont été supprimés."
        else:
            return f"⚠️ Le chemin '{path}' n'est ni un fichier ni un dossier reconnu."
    except Exception as e:
        return f"❌ Impossible de supprimer '{path}': {e}"
    

def search_files(query, path=None):
    """
    Recherche un mot ou une expression dans tous les fichiers.
    Si path=None, cherche à partir de C:/ (ou le disque courant).
    Sinon cherche dans le dossier spécifié et ses sous-dossiers.
    """
    if not query:
        return "❌ Erreur: la requête de recherche ne peut pas être vide."
    
    # Si path n'est pas fourni, chercher à partir de C:/ (Windows) ou / (Linux/Mac)
    if path is None:
        path = "C:\\" if os.name == 'nt' else "/"
    
    path = os.path.abspath(path)
    
    results = []
    max_results = 50  # Limiter le nombre de résultats pour éviter un débordement

    try:
        for root, dirs, files in os.walk(path):
            if len(results) >= max_results:
                break
            for file in files:
                if len(results) >= max_results:
                    break
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        for i, line in enumerate(f, 1):
                            if query.lower() in line.lower():
                                results.append(f"{file_path} (ligne {i}): {line.strip()}")
                                if len(results) >= max_results:
                                    break
                except Exception:
                    # ignore les fichiers non lisibles ou binaires
                    continue
    except PermissionError:
        return f"⚠️ Accès refusé lors de la recherche dans '{path}'."
    except Exception as e:
        return f"❌ Erreur lors de la recherche: {e}"

    if results:
        return "\n".join(results[:max_results]) + (f"\n\n... (limité à {max_results} résultats)" if len(results) >= max_results else "")
    else:
        return f"⚠️ Aucun résultat trouvé pour '{query}' dans '{path}'."


def open_browser(url=None, youtube_search=None):
    """
    Ouvre une URL dans le navigateur par défaut.
    
    Paramètres:
    - url: URL à ouvrir (ex: youtube.com, google.com)
    - youtube_search: Recherche sur YouTube (ex: "musique relaxante")
    """
    if youtube_search:
        # Créer une URL de recherche YouTube
        search_query = youtube_search.replace(" ", "+")
        url = f"https://www.youtube.com/results?search_query={search_query}"
    
    if not url:
        return "❌ Erreur: fournissez une URL ou une recherche YouTube."
    
    # Ajouter le protocole si absent
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    
    try:
        webbrowser.open(url)
        return f"✅ Navigation vers {url} en cours..."
    except Exception as e:
        return f"❌ Impossible d'ouvrir le navigateur: {e}"






def git_push(commit_message="Automated commit", branch=None):
    """
    Effectue git add ., git commit et git push.
    
    Paramètres:
    - commit_message: Message du commit
    - branch: Branche cible (optionnel)
    
    Retourne le résultat ou un message d'erreur.
    """
    import subprocess
    
    # Vérifier qu'on est dans un dépôt Git
    try:
        subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        return "❌ Ce répertoire n'est pas un dépôt Git."
    except FileNotFoundError:
        return "❌ Git n'est pas installé ou introuvable."

    # git add .
    try:
        result = subprocess.run(["git", "add", "."], capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        return f"❌ git add a échoué: {e.stderr.strip()}"

    # Vérifier s'il y a des changements à committer
    diff = subprocess.run(["git", "diff", "--cached", "--quiet"], check=False)
    if diff.returncode == 0:
        return "ℹ️ Aucun changement à committer."

    # git commit
    try:
        result = subprocess.run(["git", "commit", "-m", commit_message], capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        return f"❌ git commit a échoué: {e.stderr.strip()}"

    # git push
    try:
        push_cmd = ["git", "push"]
        if branch:
            push_cmd.extend(["-u", "origin", branch])
        result = subprocess.run(push_cmd, capture_output=True, text=True, check=True)
        return f"✅ Commit et push exécutés avec succès.\n📝 Message: {commit_message}"
    except subprocess.CalledProcessError as e:
        return f"❌ git push a échoué: {e.stderr.strip()}"


def git_workflow(commit_message="Automated commit"):
    """
    Workflow Git complet:
    1. git add .
    2. git commit -m <message>
    3. Vérifier si on est sur main
    4. Si pas sur main: checkout main
    5. git merge <current_branch>
    6. git push
    
    Retourne le résultat ou un message d'erreur.
    """
    import subprocess
    
    # Vérifier qu'on est dans un dépôt Git
    try:
        subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        return "❌ Ce répertoire n'est pas un dépôt Git."
    except FileNotFoundError:
        return "❌ Git n'est pas installé ou introuvable."

    # 1. git add .
    try:
        subprocess.run(["git", "add", "."], capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        return f"❌ git add a échoué: {e.stderr.strip()}"

    # Vérifier s'il y a des changements à committer
    diff = subprocess.run(["git", "diff", "--cached", "--quiet"], check=False)
    if diff.returncode == 0:
        return "ℹ️ Aucun changement à committer."

    # 2. git commit
    try:
        subprocess.run(["git", "commit", "-m", commit_message], capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        return f"❌ git commit a échoué: {e.stderr.strip()}"

    # 3. Récupérer la branche actuelle
    try:
        current_branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"❌ Impossible de récupérer la branche actuelle: {e.stderr.strip()}"

    # 4. Vérifier si on est sur main
    if current_branch != "main":
        # Checkout main
        try:
            subprocess.run(["git", "checkout", "main"], capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            return f"❌ Checkout sur main a échoué: {e.stderr.strip()}"
        
        # 5. Merge de la branche précédente
        try:
            result = subprocess.run(["git", "merge", current_branch], capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            return f"⚠️ Merge a échoué (conflits?): {e.stderr.strip()}"
    
    # 6. git push
    try:
        subprocess.run(["git", "push"], capture_output=True, text=True, check=True)
        return f"✅ Workflow git complété avec succès!\n📝 Commit: {commit_message}\n🌿 Branche: {current_branch} -> main"
    except subprocess.CalledProcessError as e:
        return f"❌ git push a échoué: {e.stderr.strip()}"


def git_create_branch(branch_name):
    """
    Crée une nouvelle branche et la switch.
    
    Paramètres:
    - branch_name: Nom de la nouvelle branche
    
    Retourne le résultat ou un message d'erreur.
    """
    import subprocess
    
    # Vérifier qu'on est dans un dépôt Git
    try:
        subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        return "❌ Ce répertoire n'est pas un dépôt Git."
    except FileNotFoundError:
        return "❌ Git n'est pas installé ou introuvable."

    # Créer et checkout la branche
    try:
        subprocess.run(["git", "checkout", "-b", branch_name], capture_output=True, text=True, check=True)
        return f"✅ Branche '{branch_name}' créée et activée."
    except subprocess.CalledProcessError as e:
        if "already exists" in e.stderr.lower():
            return f"⚠️ La branche '{branch_name}' existe déjà."
        return f"❌ Erreur: {e.stderr.strip()}"


def git_checkout_branch(branch_name):
    """
    Switch vers une branche existante.
    
    Paramètres:
    - branch_name: Nom de la branche vers laquelle switcher
    
    Retourne le résultat ou un message d'erreur.
    """
    import subprocess
    
    # Vérifier qu'on est dans un dépôt Git
    try:
        subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        return "❌ Ce répertoire n'est pas un dépôt Git."
    except FileNotFoundError:
        return "❌ Git n'est pas installé ou introuvable."

    # Vérifier qu'il n'y a pas de changements non commitées
    try:
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, check=True)
        if result.stdout.strip():
            return "⚠️ Vous avez des changements non commitées. Faites un commit ou un stash avant de changer de branche."
    except subprocess.CalledProcessError:
        pass

    # Checkout la branche
    try:
        subprocess.run(["git", "checkout", branch_name], capture_output=True, text=True, check=True)
        return f"✅ Switched vers la branche '{branch_name}'."
    except subprocess.CalledProcessError as e:
        if "did not match any" in e.stderr.lower():
            return f"❌ La branche '{branch_name}' n'existe pas."
        return f"❌ Erreur: {e.stderr.strip()}"


def git_list_branches():
    """
    Liste toutes les branches du dépôt.
    
    Retourne la liste des branches ou un message d'erreur.
    """
    import subprocess
    
    # Vérifier qu'on est dans un dépôt Git
    try:
        subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        return "❌ Ce répertoire n'est pas un dépôt Git."
    except FileNotFoundError:
        return "❌ Git n'est pas installé ou introuvable."

    # Lister les branches
    try:
        result = subprocess.run(["git", "branch", "-a"], capture_output=True, text=True, check=True)
        branches = result.stdout.strip()
        if not branches:
            return "ℹ️ Aucune branche trouvée."
        return f"📋 Branches disponibles:\n{branches}"
    except subprocess.CalledProcessError as e:
        return f"❌ Erreur: {e.stderr.strip()}"

def get_pc_config():
    """
    Retourne un dictionnaire avec les infos de configuration du PC.
    """
    import platform
    
    info = {}
    uname = platform.uname()
    info["system"] = uname.system
    info["hostname"] = uname.node
    info["release"] = uname.release
    info["processor"] = uname.processor
    info["machine"] = uname.machine

    # Informations CPU et mémoire via psutil si disponible
    try:
        import psutil
        info["cpu_cores"] = psutil.cpu_count(logical=True)
        info["cpu_percent"] = psutil.cpu_percent(interval=1)
        
        mem = psutil.virtual_memory()
        info["ram_total_gb"] = round(mem.total / (1024**3), 2)
        info["ram_available_gb"] = round(mem.available / (1024**3), 2)
        info["ram_percent"] = mem.percent
        
        disk = psutil.disk_usage('/')
        info["disk_total_gb"] = round(disk.total / (1024**3), 2)
        info["disk_free_gb"] = round(disk.free / (1024**3), 2)
        info["disk_percent"] = disk.percent
    except ImportError:
        info["warning"] = "psutil non installé - infos limitées"

    return info


def install_python_package(package_name):
    """
    Installe un paquet Python via pip.
    
    Paramètres:
    - package_name: Nom du paquet à installer (ex: 'requests', 'numpy==1.21.0')
    
    Retourne le résultat ou un message d'erreur.
    """
    import sys
    import subprocess
    
    if not package_name or not package_name.strip():
        return "❌ Erreur: le nom du paquet ne peut pas être vide."
    
    package_name = package_name.strip()
    
    try:
        # Utiliser le même Python que celui qui exécute le code
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package_name],
            capture_output=True,
            text=True,
            check=True
        )
        return f"✅ Le paquet '{package_name}' a été installé avec succès.\n{result.stdout.strip()}"
    except subprocess.CalledProcessError as e:
        return f"❌ Erreur lors de l'installation de '{package_name}':\n{e.stderr.strip()}"
    except Exception as e:
        return f"❌ Erreur inattendue: {e}"


def git_clone(repo_url, target_path=None):
    """
    Clone un dépôt Git à partir d'une URL.
    
    Paramètres:
    - repo_url: URL du dépôt Git (ex: https://github.com/user/repo.git)
    - target_path: Chemin où cloner (optionnel, par défaut le Bureau/Desktop)
    
    Retourne le résultat ou un message d'erreur.
    """
    import subprocess
    
    if not repo_url or not repo_url.strip():
        return "❌ Erreur: l'URL du dépôt ne peut pas être vide."
    
    repo_url = repo_url.strip()
    
    # Vérifier que c'est une URL Git valide
    if not ("git" in repo_url.lower() or "github" in repo_url.lower() or repo_url.endswith(".git")):
        if not repo_url.startswith(("http://", "https://", "git@")):
            return "❌ Erreur: URL du dépôt invalide. Utilisez une URL HTTPS ou SSH."
    
    try:
        # Déterminer le chemin par défaut (Bureau/Desktop)
        if not target_path:
            # Récupérer le chemin du bureau
            import platform
            if platform.system() == "Windows":
                desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            else:
                desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            
            # Extraire le nom du repo de l'URL
            repo_name = repo_url.rstrip("/").split("/")[-1]
            if repo_name.endswith(".git"):
                repo_name = repo_name[:-4]
            
            target_path = os.path.join(desktop_path, repo_name)
        else:
            target_path = os.path.abspath(target_path)
        
        # Construire la commande git clone
        clone_cmd = ["git", "clone", repo_url, target_path]
        
        # Exécuter git clone
        result = subprocess.run(
            clone_cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        return f"✅ Dépôt cloné avec succès!\n📍 Chemin: {target_path}\n🔗 URL: {repo_url}"
    
    except subprocess.CalledProcessError as e:
        return f"❌ Erreur lors du clone:\n{e.stderr.strip()}"
    except FileNotFoundError:
        return "❌ Git n'est pas installé ou introuvable."
    except Exception as e:
        return f"❌ Erreur inattendue: {e}"


def launch_application(app_path, arguments=None):
    """
    Lance une application (exe, script, etc.).
    
    Paramètres:
    - app_path: Chemin complet de l'application (ex: C:\\Program Files\\app.exe, notepad.exe)
    - arguments: Arguments à passer à l'application (optionnel, ex: 'file.txt')
    
    Retourne un message de succès ou d'erreur.
    """
    import subprocess
    import platform
    
    if not app_path or not app_path.strip():
        return "❌ Erreur: le chemin de l'application ne peut pas être vide."
    
    app_path = app_path.strip()
    
    try:
        # Construire la commande
        if arguments:
            # Si des arguments sont fournis, créer une liste
            if isinstance(arguments, str):
                cmd = [app_path, arguments]
            else:
                cmd = [app_path] + arguments
        else:
            cmd = [app_path]
        
        # Lancer l'application
        # Utiliser Popen pour ne pas attendre la fin de l'application
        if platform.system() == "Windows":
            # Sur Windows, utiliser CREATE_NO_WINDOW pour éviter une console
            import subprocess
            subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
        else:
            # Sur Linux/macOS
            subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL
            )
        
        app_name = os.path.basename(app_path)
        return f"✅ L'application '{app_name}' a été lancée avec succès!\n📍 Chemin: {app_path}"
    
    except FileNotFoundError:
        return f"❌ Erreur: l'application '{app_path}' n'a pas été trouvée."
    except PermissionError:
        return f"❌ Erreur: permission refusée pour lancer '{app_path}'."
    except Exception as e:
        return f"❌ Erreur lors du lancement de l'application: {e}"

def print_file(file_path, printer_name=None):
    """Imprime un fichier sur une imprimante réseau ou locale."""
    try:
        # Gérer les chemins relatifs
        if not os.path.isabs(file_path):
            file_path = os.path.abspath(file_path)
        
        # Vérifier que le fichier existe
        if not os.path.exists(file_path):
            return f"❌ Erreur: le fichier '{file_path}' n'existe pas."
        
        file_name = os.path.basename(file_path)
        
        # Sur Windows, utiliser ShellExecute (le plus simple)
        import platform
        if platform.system() == "Windows":
            try:
                import win32api
                
                # ShellExecute avec "print" lance directement l'imprimante par défaut
                win32api.ShellExecute(0, "print", file_path, None, ".", 0)
                
                return f"✅ '{file_name}' envoyé à l'imprimante!"
            
            except ImportError:
                # Fallback sans win32api: utiliser Notepad pour imprimer
                try:
                    subprocess.run(
                        ["notepad.exe", "/p", file_path],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        timeout=5
                    )
                    return f"✅ '{file_name}' envoyé à l'imprimante!"
                except Exception as e:
                    return f"❌ Erreur impression: {e}"
            except Exception as e:
                return f"❌ Erreur: {e}"
        
        else:
            # Sur Linux/macOS, utiliser lpr
            try:
                subprocess.run(
                    ["lpr", file_path],
                    check=True,
                    capture_output=True,
                    timeout=5
                )
                return f"✅ '{file_name}' envoyé à l'imprimante!"
            except Exception as e:
                return f"❌ Erreur: {e}"
    
    except Exception as e:
        return f"❌ Erreur impression: {e}"

def search_web(query, num_results=5):
    """Recherche sur le web avec DuckDuckGo et retourne les résultats avec URLs."""
    try:
        try:
            from ddgs import DDGS
        except ImportError:
            return f"❌ Module ddgs non installé. Installe-le avec: pip install ddgs"
        
        # Utiliser DuckDuckGo qui est plus permissif que Google
        ddgs = DDGS()
        
        # Effectuer la recherche en français (région France)
        results = list(ddgs.text(query, region='fr-fr', max_results=num_results))
        
        if not results:
            return f"❌ Aucun résultat trouvé pour '{query}'"
        
        # Formater les résultats
        output = f"🔍 Résultats de recherche pour '{query}':\n\n"
        for i, result in enumerate(results, 5):
            title = result.get('title', 'Sans titre')
            url = result.get('href', '#')
            body = result.get('body', 'Pas de description')
            
            output += f"{i}. **{title}**\n"
            output += f"   🔗 {url}\n"
            output += f"   📝 {body[:150]}...\n\n"
        
        return output
    
    except Exception as e:
        return f"❌ Erreur lors de la recherche web: {str(e)}"

def fetch_webpage(url):
    """Récupère et extrait le contenu textuel d'une page web avec Trafilatura."""
    try:
        import trafilatura
        
        # Valider l'URL
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Télécharger la page
        response = requests.get(url, timeout=15, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        
        # Extraire le contenu avec trafilatura
        content = trafilatura.extract(response.text, include_comments=False, favor_precision=True)
        
        if not content:
            return f"❌ Impossible d'extraire le contenu de {url}"
        
        # Limiter à 4000 caractères pour éviter de dépasser les limites de tokens
        if len(content) > 4000:
            content = content[:4000] + "\n\n[...contenu tronqué...]"
        
        # Récupérer le titre
        metadata = trafilatura.extract_metadata(response.text)
        title = metadata.title if metadata and metadata.title else "Sans titre"
        
        output = f"📄 Contenu de: {url}\n"
        output += f"📋 Titre: {title}\n"
        output += f"{'='*60}\n\n"
        output += content
        
        return output
    
    except requests.exceptions.ConnectionError:
        return f"❌ Erreur de connexion: impossible d'accéder à {url}"
    except requests.exceptions.Timeout:
        return f"❌ Timeout: la page met trop de temps à charger"
    except requests.exceptions.HTTPError as e:
        return f"❌ Erreur HTTP {e.response.status_code}: {url}"
    except Exception as e:
        return f"❌ Erreur lors de la récupération de la page: {e}"

def search_and_summarize(query):
    """Recherche sur le web et extrait le contenu en texte de la page la plus pertinente."""
    try:
        # D'abord, faire une recherche avec plusieurs résultats
        search_results = search_web(query, num_results=5)
        
        if "❌" in search_results or "⚠️" in search_results:
            return search_results
        
        # Extraire toutes les URLs et titres des résultats
        import re
        urls = re.findall(r'🔗 (https?://[^\s\)]+)', search_results)
        titles = re.findall(r'\*\*([^*]+)\*\*', search_results)
        
        if not urls:
            return search_results  # Retourner juste les résultats si pas d'URL
        
        # Trouver la page la plus pertinente (correspondance avec la query)
        query_words = query.lower().split()
        best_url = urls[0]
        best_score = 0
        
        for i, (url, title) in enumerate(zip(urls, titles)):
            title_lower = title.lower()
            # Score basé sur les mots de la query présents dans le titre
            score = sum(1 for word in query_words if word in title_lower)
            # Bonus si le titre commence par un mot de la query
            if any(title_lower.startswith(word) for word in query_words):
                score += 2
            # Bonus pour Wikipedia (généralement plus fiable)
            if "wikipedia" in url.lower():
                score += 1
            # Pénalité pour les pages qui semblent être des variantes (III, Jr, etc.)
            if any(x in title for x in [" III", " II", " Jr", " Sr", "frère", "fils", "neveu"]):
                if not any(x in query for x in ["III", "II", "Jr", "frère", "fils", "neveu"]):
                    score -= 2
            
            if score > best_score:
                best_score = score
                best_url = url
        
        # Récupérer le contenu de la page la plus pertinente
        content = fetch_webpage(best_url)
        
        return f"📄 Source: {best_url}\n\n{content}"
    
    except Exception as e:
        return f"❌ Erreur lors de la recherche et résumé: {e}"