
"""
Modèles Cart - Panier d'achat
"""

from sqlalchemy import (
    Column, BigInteger, Integer, DECIMAL, ForeignKey
)
from sqlalchemy.orm import relationship
from typing import Optional

from app.models.base import BaseModel


class Cart(BaseModel):
    """
    Modèle Cart - Panier d'achat utilisateur
    
    Relations:
        - user: Propriétaire du panier (N-1)
        - items: Articles dans le panier (1-N)
    """
    
    __tablename__ = "carts"
    
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
        unique=True,  # Un utilisateur = un panier
        index=True,
        comment="Identifiant de l'utilisateur"
    )
    
    # ===== Relations =====
    user = relationship(
        "User",
        back_populates="carts"
    )
    
    items = relationship(
        "CartItem",
        back_populates="cart",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    # ===== Propriétés calculées =====
    @property
    def total_items(self) -> int:
        """Nombre total d'articles dans le panier"""
        if not self.items:
            return 0
        return sum(item.quantity for item in self.items)
    
    @property
    def subtotal(self) -> float:
        """Sous-total du panier (sans frais)"""
        if not self.items:
            return 0.0
        return sum(item.subtotal for item in self.items)
    
    @property
    def is_empty(self) -> bool:
        """Vérifie si le panier est vide"""
        return len(self.items) == 0 if self.items else True
    
    def __repr__(self) -> str:
        return f"<Cart(id={self.id}, user_id={self.user_id}, items={self.total_items})>"


class CartItem(BaseModel):
    """
    Modèle CartItem - Article dans le panier
    
    Relations:
        - cart: Panier contenant cet article (N-1)
        - product: Produit ajouté (N-1)
    """
    
    __tablename__ = "cart_items"
    
    # ===== Colonnes =====
    id = Column(
        BigInteger().with_variant(BigInteger, "sqlite"),
        primary_key=True,
        autoincrement=True,
        comment="Identifiant unique"
    )
    
    cart_id = Column(
        BigInteger,
        ForeignKey("carts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Identifiant du panier"
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
        default=1,
        comment="Quantité"
    )
    
    price = Column(
        DECIMAL(12, 2),
        nullable=False,
        comment="Prix unitaire au moment de l'ajout"
    )
    
    # ===== Relations =====
    cart = relationship(
        "Cart",
        back_populates="items"
    )
    
    product = relationship(
        "Product",
        back_populates="cart_items",
        lazy="joined"
    )
    
    # ===== Propriétés calculées =====
    @property
    def subtotal(self) -> float:
        """Sous-total de cet article (quantité × prix)"""
        return float(self.price) * self.quantity
    
    @property
    def is_available(self) -> bool:
        """Vérifie si le produit est toujours disponible en stock"""
        if not self.product:
            return False
        return self.product.is_active and self.product.stock >= self.quantity
    
    def __repr__(self) -> str:
        return f"<CartItem(id={self.id}, product_id={self.product_id}, quantity={self.quantity})>"