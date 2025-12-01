import os

def list_files(path="."):
    return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"{path} mis à jour"
