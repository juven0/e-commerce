import os
from pathlib import Path
import hashlib
import re

REPO_PATH = "./node-express-boilerplate"
SUPORTED_EXT = [".js", ".md", ".yml", "yaml"]

def get_file(path):
    files = []
    for root, dirs, filenames in os.walk(path):
        for file in filenames:
            if any(file.endswith(ext) for ext in SUPORTED_EXT):
                files.append(os.path.join(root,file))
    return files

def read_file(file_path):
    with open(file_path, "r", encoding= "utf-8") as f:
        return f.read()

def chunk_js_findall(content):

    pattern = r"(function\s+\w+\s*\([^\)]*\)\s*{[^}]*})|((?:const|let|var)\s+\w+\s*=\s*\([^\)]*\)\s*=>\s*{[^}]*})"
    matches = re.findall(pattern, content, re.DOTALL)
    chunks = []

    for m in matches:
        chunk_text = m[0] if m[0] else m[1]
        if len(chunk_text.strip()) > 20:
            chunks.append(chunk_text.strip())
    return chunks

def compute_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def process_chunk():
    points = []

    for file_path in get_file(REPO_PATH):
        content = read_file(file_path)
        ext = Path(file_path).suffix

        if ext == ".js":
            chunks = chunk_js_findall(content)
        else:
            chunks = [content]

        for chunk in chunks:
            chunk_hash = compute_hash(chunk)
            
            metadata = {
                "file": os.path.relpath(file_path, REPO_PATH),
                "repo": Path(REPO_PATH).name,
                "hash": chunk_hash,
                "type": "function" if ext == ".js" else "doc"
            }

            print(metadata)
