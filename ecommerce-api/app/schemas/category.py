
"""
Schemas Pydantic pour Category
Validation et sérialisation des catégories
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from slugify import slugify


# ===== Schemas de base =====
class CategoryBase(BaseModel):
    """Schema de base pour Category"""
    name: str = Field(..., min_length=1, max_length=150, description="Nom de la catégorie")
    description: Optional[str] = Field(None, description="Description")
    is_active: bool = Field(default=True, description="Catégorie active")


# ===== Schemas de création =====
class CategoryCreate(CategoryBase):
    """Schema pour créer une catégorie"""
    parent_id: Optional[int] = Field(None, description="ID de la catégorie parente")
    slug: Optional[str] = Field(None, max_length=191, description="Slug (généré auto si non fourni)")
    
    @field_validator("slug", mode="before")
    @classmethod
    def generate_slug(cls, v: Optional[str], info) -> str:
        """Génère automatiquement le slug si non fourni"""
        if v:
            return slugify(v)
        # Si pas de slug fourni, on utilise le name
        name = info.data.get("name")
        if name:
            return slugify(name)
        return ""


# ===== Schemas de mise à jour =====
class CategoryUpdate(BaseModel):
    """Schema pour mettre à jour une catégorie"""
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    slug: Optional[str] = Field(None, max_length=191)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: Optional[bool] = None
    
    @field_validator("slug", mode="before")
    @classmethod
    def validate_slug(cls, v: Optional[str]) -> Optional[str]:
        """Valide et slugifie si nécessaire"""
        if v:
            return slugify(v)
        return v


# ===== Schemas de réponse =====
class CategoryResponse(CategoryBase):
    """Schema de réponse pour une catégorie"""
    id: int
    parent_id: Optional[int] = None
    slug: str
    created_at: datetime
    
    model_config = {
        "from_attributes": True
    }


class CategoryWithChildrenResponse(CategoryResponse):
    """Schema de réponse avec sous-catégories"""
    children: List["CategoryResponse"] = []
    
    model_config = {
        "from_attributes": True
    }


class CategoryWithParentResponse(CategoryResponse):
    """Schema de réponse avec catégorie parente"""
    parent: Optional[CategoryResponse] = None
    
    model_config = {
        "from_attributes": True
    }


class CategoryTreeResponse(CategoryResponse):
    """Schema de réponse pour arbre de catégories"""
    children: List["CategoryTreeResponse"] = []
    level: int = 0
    
    model_config = {
        "from_attributes": True
    }


class CategoryListResponse(BaseModel):
    """Schema de réponse pour liste de catégories"""
    categories: list[CategoryResponse]
    total: int
    page: Optional[int] = None
    page_size: Optional[int] = None


# ===== Schemas pour filtrage =====
class CategoryFilterParams(BaseModel):
    """Paramètres de filtrage des catégories"""
    parent_id: Optional[int] = Field(None, description="Filtrer par catégorie parente")
    is_active: Optional[bool] = Field(None, description="Filtrer par statut actif")
    search: Optional[str] = Field(None, description="Recherche par nom")


# Résoudre les références forward
CategoryWithChildrenResponse.model_rebuild()
CategoryTreeResponse.model_rebuild()