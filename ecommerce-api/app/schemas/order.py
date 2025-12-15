
"""
Schemas Pydantic pour Order
Validation et sérialisation des commandes
"""

from pydantic import BaseModel, Field, computed_field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

from app.models.order import OrderStatus


# ===== Schemas pour OrderItem =====
class OrderItemBase(BaseModel):
    """Schema de base pour OrderItem"""
    product_id: int
    quantity: int = Field(..., gt=0)
    unit_price: Decimal


class OrderItemResponse(BaseModel):
    """Schema de réponse pour un article de commande"""
    id: int
    order_id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    created_at: datetime
    updated_at: datetime
    
    # Informations du produit
    product: Optional["ProductOrderResponse"] = None
    
    model_config = {
        "from_attributes": True
    }
    
    @computed_field
    @property
    def subtotal(self) -> float:
        """Sous-total de l'article"""
        return float(self.unit_price) * self.quantity


class ProductOrderResponse(BaseModel):
    """Schema simplifié de produit dans une commande"""
    id: int
    name: str
    slug: str
    sku: Optional[str] = None
    
    model_config = {
        "from_attributes": True
    }


# ===== Schemas de création de commande =====
class OrderCreate(BaseModel):
    """Schema pour créer une commande"""
    billing_address_id: int = Field(..., description="ID adresse de facturation")
    shipping_address_id: int = Field(..., description="ID adresse de livraison")
    coupon_code: Optional[str] = Field(None, description="Code promo (optionnel)")


class OrderFromCart(BaseModel):
    """Schema pour créer une commande depuis le panier"""
    billing_address_id: int
    shipping_address_id: int
    coupon_code: Optional[str] = None


# ===== Schemas de mise à jour =====
class OrderUpdateStatus(BaseModel):
    """Schema pour mettre à jour le statut (admin)"""
    status: OrderStatus = Field(..., description="Nouveau statut")


class OrderCancel(BaseModel):
    """Schema pour annuler une commande"""
    reason: Optional[str] = Field(None, description="Raison de l'annulation")


# ===== Schemas de réponse =====
class OrderResponse(BaseModel):
    """Schema de réponse pour une commande"""
    id: int
    user_id: int
    status: OrderStatus
    total_amount: Decimal
    billing_address_id: Optional[int] = None
    shipping_address_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = {
        "from_attributes": True
    }
    
    @computed_field
    @property
    def is_paid(self) -> bool:
        """Commande payée"""
        return self.status in [OrderStatus.PAID, OrderStatus.SHIPPED, OrderStatus.DELIVERED]
    
    @computed_field
    @property
    def is_delivered(self) -> bool:
        """Commande livrée"""
        return self.status == OrderStatus.DELIVERED
    
    @computed_field
    @property
    def can_be_cancelled(self) -> bool:
        """Peut être annulée"""
        return self.status in [OrderStatus.PENDING, OrderStatus.PAID]


class OrderDetailResponse(OrderResponse):
    """Schema de réponse détaillé avec relations"""
    items: List[OrderItemResponse] = []
    billing_address: Optional["AddressResponse"] = None
    shipping_address: Optional["AddressResponse"] = None
    payments: List["PaymentResponse"] = []
    
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
        """Sous-total"""
        return sum(item.subtotal for item in self.items)


class OrderListResponse(BaseModel):
    """Schema de réponse pour liste de commandes"""
    orders: list[OrderResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ===== Schemas pour filtrage =====
class OrderFilterParams(BaseModel):
    """Paramètres de filtrage des commandes"""
    status: Optional[OrderStatus] = Field(None, description="Filtrer par statut")
    user_id: Optional[int] = Field(None, description="Filtrer par utilisateur (admin)")
    from_date: Optional[datetime] = Field(None, description="Date de début")
    to_date: Optional[datetime] = Field(None, description="Date de fin")
    min_amount: Optional[Decimal] = Field(None, description="Montant minimum")
    max_amount: Optional[Decimal] = Field(None, description="Montant maximum")


# ===== Schemas de confirmation =====
class OrderCreatedResponse(BaseModel):
    """Réponse après création de commande"""
    order: OrderDetailResponse
    message: str = "Commande créée avec succès"
    payment_required: bool = True


class OrderCancelledResponse(BaseModel):
    """Réponse après annulation"""
    message: str = "Commande annulée"
    success: bool = True
    order_id: int


# Import pour résoudre les références forward
from app.schemas.address import AddressResponse
from app.schemas.payment import PaymentResponse

OrderItemResponse.model_rebuild()
OrderDetailResponse.model_rebuild()