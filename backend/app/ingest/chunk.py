from dataclasses import dataclass, field
from typing import List, Optional, Dict
import uuid

@dataclass
class Chunk:
    id: str = field(default_factory=lambda: str(uuid.uuid4))
    name: Optional[str] = None
    type: str = "unknown"
    language: str = "unknown"
    path: str = ""
    code: str = ""
    params: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    # exported: bool = False
    role: Optional[str] = None
    summary: Optional[str] = None
    metadata: dict[str, str] = field(default_factory=dict)

    def to_embedding(self):
        parts = [
            f"Type: {self.type}",
            f"Nom: {self.name}",
            f"Langage: {self.language}",
            f"Fichier: {self.file_path}",
            
        ]

        if self.role:
            parts.append(f"Role: {self.role}")

        if self.params:
            parts.append(f"Paramètres: {', '.join(self.params)}")

        if self.imports:
            parts.append(f"Imports: {', '.join(self.imports)}")

        if self.summary:
            parts.append(f"Résumé: {self.summary}")

        parts.append("Code:")
        parts.append(self.code)

        return "\n".join(parts)
