
"""
Schemas Pydantic pour Cart
Validation et sérialisation du panier
"""

from pydantic import BaseModel, Field, computed_field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# ===== Schemas pour CartItem =====
class CartItemBase(BaseModel):
    """Schema de base pour CartItem"""
    product_id: int = Field(..., gt=0, description="ID du produit")
    quantity: int = Field(..., gt=0, description="Quantité")


class CartItemCreate(CartItemBase):
    """Schema pour ajouter un article au panier"""
    pass


class CartItemUpdate(BaseModel):
    """Schema pour mettre à jour un article du panier"""
    quantity: int = Field(..., gt=0, description="Nouvelle quantité")


class CartItemResponse(BaseModel):
    """Schema de réponse pour un article du panier"""
    id: int
    cart_id: int
    product_id: int
    quantity: int
    price: Decimal
    created_at: datetime
    updated_at: datetime
    
    # Informations du produit (nested)
    product: Optional["ProductCartResponse"] = None
    
    model_config = {
        "from_attributes": True
    }
    
    @computed_field
    @property
    def subtotal(self) -> float:
        """Sous-total de l'article"""
        return float(self.price) * self.quantity


# ===== Schema simplifié de produit pour le panier =====
class ProductCartResponse(BaseModel):
    """Schema simplifié de produit dans le panier"""
    id: int
    name: str
    slug: str
    price: Decimal
    sale_price: Optional[Decimal] = None
    stock: int
    is_active: bool
    
    model_config = {
        "from_attributes": True
    }
    
    @computed_field
    @property
    def current_price(self) -> float:
        """Prix actuel"""
        if self.sale_price and self.sale_price > 0:
            return float(self.sale_price)
        return float(self.price)
    
    @computed_field
    @property
    def is_available(self) -> bool:
        """Produit disponible"""
        return self.is_active and self.stock > 0


# ===== Schemas pour Cart =====
class CartResponse(BaseModel):
    """Schema de réponse pour le panier"""
    id: int
    user_id: int
    items: List[CartItemResponse] = []
    created_at: datetime
    updated_at: datetime
    
    model_config = {
        "from_attributes": True
    }
    
    @computed_field
    @property
    def total_items(self) -> int:
        """Nombre total d'articles"""
        return sum(item.quantity for item in self.items)
    
    @computed_field
    @property
    def subtotal(self) -> float:
        """Sous-total du panier"""
        return sum(item.subtotal for item in self.items)
    
    @computed_field
    @property
    def is_empty(self) -> bool:
        """Panier vide"""
        return len(self.items) == 0


class CartSummaryResponse(BaseModel):
    """Schema de résumé du panier (sans détails des produits)"""
    total_items: int
    subtotal: float
    items_count: int


# ===== Schemas pour actions sur le panier =====
class AddToCartRequest(CartItemCreate):
    """Requête pour ajouter au panier"""
    pass


class UpdateCartItemRequest(CartItemUpdate):
    """Requête pour mettre à jour un article"""
    pass


class RemoveFromCartResponse(BaseModel):
    """Réponse après suppression d'un article"""
    message: str = "Article retiré du panier"
    success: bool = True


class ClearCartResponse(BaseModel):
    """Réponse après vidage du panier"""
    message: str = "Panier vidé"
    success: bool = True


# Résoudre les références forward
CartItemResponse.model_rebuild()