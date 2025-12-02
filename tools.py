import os
import shutil
import webbrowser
import subprocess

def list_files(path="."):
    """Liste tous les fichiers d'un dossier (exclut les dossiers)."""
    try:
        path = os.path.abspath(path)
        return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    except FileNotFoundError:
        return f"Erreur: le chemin '{path}' n'existe pas."
    except PermissionError:
        return f"Erreur: accès refusé à '{path}'."

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
