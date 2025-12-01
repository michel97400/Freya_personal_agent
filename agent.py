from tools import list_files, read_file, write_file

class FreyaAgent:
    def __init__(self):
        self.memory = []

    def respond(self, message):
        message = message.lower()
        if "liste fichiers" in message:
            files = list_files()
            return "Fichiers:\n" + "\n".join(files)
        elif "lire" in message:
            filename = message.split("lire ")[-1]
            try:
                content = read_file(filename)
                return f"Contenu de {filename}:\n{content[:500]}..."  # extrait limité
            except FileNotFoundError:
                return f"Fichier {filename} non trouvé."
        else:
            return "Je peux lister des fichiers ou lire un fichier. Essaie 'liste fichiers' ou 'lire <nom_du_fichier>'."
