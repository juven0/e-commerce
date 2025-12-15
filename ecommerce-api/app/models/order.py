
"""
Modèles Order - Commandes
"""

from sqlalchemy import (
    Column, BigInteger, Integer, DECIMAL, Enum, ForeignKey, Table
)
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel
from app.core.database import Base


class OrderStatus(str, enum.Enum):
    """Statuts de commande"""
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


# ===== Table d'association commandes <-> coupons =====
order_coupons = Table(
    "order_coupons",
    Base.metadata,
    Column(
        "order_id",
        BigInteger,
        ForeignKey("orders.id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "coupon_id",
        BigInteger,
        ForeignKey("coupons.id", ondelete="CASCADE"),
        primary_key=True
    )
)


class Order(BaseModel):
    """
    Modèle Order - Commandes
    
    Relations:
        - user: Client ayant passé la commande (N-1)
        - items: Articles de la commande (1-N)
        - payments: Paiements associés (1-N)
        - billing_address: Adresse de facturation (N-1)
        - shipping_address: Adresse de livraison (N-1)
        - coupons: Coupons appliqués (N-N)
    """
    
    __tablename__ = "orders"
    
    # ===== Colonnes =====
    id = Column(
        BigInteger().with_variant(BigInteger, "sqlite"),
        primary_key=True,
        autoincrement=True,
        comment="Identifiant unique"
    )
    
    user_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Identifiant du client"
    )
    
    status = Column(
        Enum(OrderStatus),
        default=OrderStatus.PENDING,
        nullable=False,
        index=True,
        comment="Statut de la commande"
    )
    
    total_amount = Column(
        DECIMAL(12, 2),
        nullable=False,
        comment="Montant total TTC"
    )
    
    billing_address_id = Column(
        BigInteger,
        ForeignKey("addresses.id", ondelete="SET NULL"),
        nullable=True,
        comment="Adresse de facturation"
    )
    
    shipping_address_id = Column(
        BigInteger,
        ForeignKey("addresses.id", ondelete="SET NULL"),
        nullable=True,
        comment="Adresse de livraison"
    )
    
    # ===== Relations =====
    user = relationship(
        "User",
        back_populates="orders"
    )
    
    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    payments = relationship(
        "Payment",
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    billing_address = relationship(
        "Address",
        foreign_keys=[billing_address_id],
        back_populates="billing_orders"
    )
    
    shipping_address = relationship(
        "Address",
        foreign_keys=[shipping_address_id],
        back_populates="shipping_orders"
    )
    
    coupons = relationship(
        "Coupon",
        secondary=order_coupons,
        back_populates="orders"
    )
    
    # ===== Propriétés calculées =====
    @property
    def total_items(self) -> int:
        """Nombre total d'articles"""
        if not self.items:
            return 0
        return sum(item.quantity for item in self.items)
    
    @property
    def subtotal(self) -> float:
        """Sous-total avant réductions"""
        if not self.items:
            return 0.0
        return sum(item.subtotal for item in self.items)
    
    @property
    def is_paid(self) -> bool:
        """Vérifie si la commande est payée"""
        return self.status in [OrderStatus.PAID, OrderStatus.SHIPPED, OrderStatus.DELIVERED]
    
    @property
    def is_delivered(self) -> bool:
        """Vérifie si la commande est livrée"""
        return self.status == OrderStatus.DELIVERED
    
    @property
    def is_cancelled(self) -> bool:
        """Vérifie si la commande est annulée"""
        return self.status == OrderStatus.CANCELLED
    
    @property
    def can_be_cancelled(self) -> bool:
        """Vérifie si la commande peut être annulée"""
        return self.status in [OrderStatus.PENDING, OrderStatus.PAID]
    
    def __repr__(self) -> str:
        return f"<Order(id={self.id}, user_id={self.user_id}, status='{self.status}', total={self.total_amount})>"


class OrderItem(BaseModel):
    """
    Modèle OrderItem - Article de commande
    
    Relations:
        - order: Commande contenant cet article (N-1)
        - product: Produit commandé (N-1)
    """
    
    __tablename__ = "order_items"
    
    # ===== Colonnes =====
    id = Column(
        BigInteger().with_variant(BigInteger, "sqlite"),
        primary_key=True,
        autoincrement=True,
        comment="Identifiant unique"
    )
    
    order_id = Column(
        BigInteger,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Identifiant de la commande"
    )
    
    product_id = Column(
        BigInteger,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Identifiant du produit"
    )
    
    quantity = Column(
        Integer,
        nullable=False,
        comment="Quantité commandée"
    )
    
    unit_price = Column(
        DECIMAL(12, 2),
        nullable=False,
        comment="Prix unitaire au moment de la commande"
    )
    
    # ===== Relations =====
    order = relationship(
        "Order",
        back_populates="items"
    )
    
    product = relationship(
        "Product",
        back_populates="order_items",
        lazy="joined"
    )
    
    # ===== Propriétés calculées =====
    @property
    def subtotal(self) -> float:
        """Sous-total de cet article"""
        return float(self.unit_price) * self.quantity
    
    def __repr__(self) -> str:
        return f"<OrderItem(id={self.id}, order_id={self.order_id}, product_id={self.product_id}, qty={self.quantity})>"