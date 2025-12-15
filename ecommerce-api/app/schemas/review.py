
"""
Schemas Pydantic pour Review
Validation et sérialisation des avis clients
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


# ===== Schemas de base =====
class ReviewBase(BaseModel):
    """Schema de base pour Review"""
    rating: int = Field(..., ge=1, le=5, description="Note de 1 à 5")
    comment: Optional[str] = Field(None, max_length=2000, description="Commentaire")


# ===== Schemas de création =====
class ReviewCreate(ReviewBase):
    """Schema pour créer un avis"""
    product_id: int = Field(..., description="ID du produit")
    
    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v: int) -> int:
        """Valide que la note est entre 1 et 5"""
        if not 1 <= v <= 5:
            raise ValueError("La note doit être entre 1 et 5")
        return v


# ===== Schemas de mise à jour =====
class ReviewUpdate(BaseModel):
    """Schema pour mettre à jour un avis"""
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=2000)
    
    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v: Optional[int]) -> Optional[int]:
        """Valide la note si fournie"""
        if v is not None and not 1 <= v <= 5:
            raise ValueError("La note doit être entre 1 et 5")
        return v


class ReviewApprove(BaseModel):
    """Schema pour approuver un avis (admin)"""
    is_approved: bool = Field(..., description="Approuvé ou non")


# ===== Schemas de réponse =====
class ReviewResponse(ReviewBase):
    """Schema de réponse pour un avis"""
    id: int
    product_id: int
    user_id: int
    is_approved: bool
    created_at: datetime
    
    model_config = {
        "from_attributes": True
    }


class ReviewDetailResponse(ReviewResponse):
    """Schema de réponse détaillé avec relations"""
    user: Optional["UserPublicResponse"] = None
    product: Optional["ProductBasicResponse"] = None
    
    model_config = {
        "from_attributes": True
    }


class ProductBasicResponse(BaseModel):
    """Schema simplifié de produit pour avis"""
    id: int
    name: str
    slug: str
    
    model_config = {
        "from_attributes": True
    }


# ===== Schemas de liste =====
class ReviewListResponse(BaseModel):
    """Liste d'avis"""
    reviews: list[ReviewDetailResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    average_rating: Optional[float] = None


# ===== Schemas pour filtrage =====
class ReviewFilterParams(BaseModel):
    """Paramètres de filtrage des avis"""
    product_id: Optional[int] = Field(None, description="Filtrer par produit")
    user_id: Optional[int] = Field(None, description="Filtrer par utilisateur")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Filtrer par note")
    is_approved: Optional[bool] = Field(True, description="Avis approuvés uniquement")


# ===== Schemas de statistiques =====
class ReviewStats(BaseModel):
    """Statistiques d'avis pour un produit"""
    average_rating: float = Field(..., description="Note moyenne")
    total_reviews: int = Field(..., description="Nombre total d'avis")
    rating_distribution: dict[int, int] = Field(
        ..., 
        description="Distribution des notes (1-5 étoiles)"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "average_rating": 4.5,
                "total_reviews": 150,
                "rating_distribution": {
                    "5": 100,
                    "4": 30,
                    "3": 15,
                    "2": 3,
                    "1": 2
                }
            }
        }
    }


# Import pour résoudre les références forward
from app.schemas.user import UserPublicResponse

ReviewDetailResponse.model_rebuild()