
"""
Schemas Pydantic pour Product
Validation et sérialisation des produits
"""

from pydantic import BaseModel, Field, field_validator, computed_field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from slugify import slugify


# ===== Schemas pour ProductImage =====
class ProductImageBase(BaseModel):
    """Schema de base pour ProductImage"""
    image_url: str = Field(..., max_length=255, description="URL de l'image")
    is_main: bool = Field(default=False, description="Image principale")


class ProductImageCreate(ProductImageBase):
    """Schema pour créer une image produit"""
    pass


class ProductImageResponse(ProductImageBase):
    """Schema de réponse pour une image produit"""
    id: int
    product_id: int
    created_at: datetime
    
    model_config = {
        "from_attributes": True
    }


# ===== Schemas de base pour Product =====
class ProductBase(BaseModel):
    """Schema de base pour Product"""
    name: str = Field(..., min_length=1, max_length=200, description="Nom du produit")
    description: Optional[str] = Field(None, description="Description")
    price: Decimal = Field(..., gt=0, decimal_places=2, description="Prix")
    sale_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2, description="Prix promo")
    stock: int = Field(default=0, ge=0, description="Stock disponible")
    is_active: bool = Field(default=True, description="Produit actif")
    
    @field_validator("sale_price")
    @classmethod
    def validate_sale_price(cls, v: Optional[Decimal], info) -> Optional[Decimal]:
        """Valide que le prix promo est inférieur au prix normal"""
        if v is not None:
            price = info.data.get("price")
            if price and v >= price:
                raise ValueError("Le prix promotionnel doit être inférieur au prix normal")
        return v


# ===== Schemas de création =====
class ProductCreate(ProductBase):
    """Schema pour créer un produit"""
    sku: Optional[str] = Field(None, max_length=100, description="Référence produit")
    slug: Optional[str] = Field(None, max_length=191, description="Slug (auto si non fourni)")
    category_ids: List[int] = Field(default=[], description="IDs des catégories")
    
    @field_validator("slug", mode="before")
    @classmethod
    def generate_slug(cls, v: Optional[str], info) -> str:
        """Génère automatiquement le slug"""
        if v:
            return slugify(v)
        name = info.data.get("name")
        if name:
            return slugify(name)
        return ""


# ===== Schemas de mise à jour =====
class ProductUpdate(BaseModel):
    """Schema pour mettre à jour un produit"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    slug: Optional[str] = Field(None, max_length=191)
    description: Optional[str] = None
    sku: Optional[str] = Field(None, max_length=100)
    price: Optional[Decimal] = Field(None, gt=0)
    sale_price: Optional[Decimal] = Field(None, ge=0)
    stock: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    category_ids: Optional[List[int]] = None
    
    @field_validator("slug", mode="before")
    @classmethod
    def validate_slug(cls, v: Optional[str]) -> Optional[str]:
        """Slugifie si nécessaire"""
        if v:
            return slugify(v)
        return v


class ProductUpdateStock(BaseModel):
    """Schema pour mettre à jour le stock uniquement"""
    stock: int = Field(..., ge=0, description="Nouveau stock")


# ===== Schemas de réponse =====
class ProductResponse(ProductBase):
    """Schema de réponse pour un produit"""
    id: int
    slug: str
    sku: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = {
        "from_attributes": True
    }
    
    @computed_field
    @property
    def current_price(self) -> float:
        """Prix actuel (promo si disponible)"""
        if self.sale_price and self.sale_price > 0:
            return float(self.sale_price)
        return float(self.price)
    
    @computed_field
    @property
    def has_discount(self) -> bool:
        """A une promotion"""
        return self.sale_price is not None and self.sale_price > 0
    
    @computed_field
    @property
    def is_in_stock(self) -> bool:
        """En stock"""
        return self.stock > 0


class ProductDetailResponse(ProductResponse):
    """Schema de réponse détaillé avec relations"""
    images: List[ProductImageResponse] = []
    categories: List["CategoryResponse"] = []
    average_rating: Optional[float] = None
    review_count: int = 0
    
    model_config = {
        "from_attributes": True
    }


class ProductListResponse(BaseModel):
    """Schema de réponse pour liste de produits"""
    products: list[ProductResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ===== Schemas pour filtrage et recherche =====
class ProductFilterParams(BaseModel):
    """Paramètres de filtrage des produits"""
    category_id: Optional[int] = Field(None, description="Filtrer par catégorie")
    min_price: Optional[Decimal] = Field(None, ge=0, description="Prix minimum")
    max_price: Optional[Decimal] = Field(None, ge=0, description="Prix maximum")
    in_stock: Optional[bool] = Field(None, description="En stock uniquement")
    on_sale: Optional[bool] = Field(None, description="En promotion uniquement")
    is_active: Optional[bool] = Field(True, description="Produits actifs")
    search: Optional[str] = Field(None, description="Recherche par nom/description")
    sort_by: Optional[str] = Field("created_at", description="Trier par (price, name, created_at)")
    sort_order: Optional[str] = Field("desc", description="Ordre (asc, desc)")


# Import pour résoudre les références forward
from app.schemas.category import CategoryResponse

ProductDetailResponse.model_rebuild()