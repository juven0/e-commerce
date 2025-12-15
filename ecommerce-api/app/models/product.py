
"""
Modèles Product - Produits et images
"""

from sqlalchemy import (
    Column, BigInteger, String, Text, DECIMAL, Integer, Boolean,
    ForeignKey, DateTime, func, Table
)
from sqlalchemy.orm import relationship
from typing import Optional

from app.models.base import BaseModel
from app.core.database import Base


# ===== Table d'association produits <-> catégories =====
product_categories = Table(
    "product_categories",
    Base.metadata,
    Column(
        "product_id",
        BigInteger,
        ForeignKey("products.id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "category_id",
        BigInteger,
        ForeignKey("categories.id", ondelete="CASCADE"),
        primary_key=True
    )
)


class Product(BaseModel):
    """
    Modèle Product - Produits
    
    Relations:
        - categories: Catégories du produit (N-N)
        - images: Images du produit (1-N)
        - cart_items: Items de panier contenant ce produit (1-N)
        - order_items: Items de commande contenant ce produit (1-N)
        - reviews: Avis clients sur ce produit (1-N)
    """
    
    __tablename__ = "products"
    
    # ===== Colonnes =====
    id = Column(
        BigInteger().with_variant(BigInteger, "sqlite"),
        primary_key=True,
        autoincrement=True,
        comment="Identifiant unique"
    )
    
    name = Column(
        String(200),
        nullable=False,
        comment="Nom du produit"
    )
    
    slug = Column(
        String(191),
        unique=True,
        nullable=False,
        index=True,
        comment="Slug pour URL (SEO)"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="Description complète du produit"
    )
    
    sku = Column(
        String(100),
        unique=True,
        nullable=True,
        index=True,
        comment="Référence produit (Stock Keeping Unit)"
    )
    
    price = Column(
        DECIMAL(12, 2),
        nullable=False,
        comment="Prix normal"
    )
    
    sale_price = Column(
        DECIMAL(12, 2),
        nullable=True,
        comment="Prix promotionnel (optionnel)"
    )
    
    stock = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Quantité en stock"
    )
    
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Produit actif ou désactivé"
    )
    
    # ===== Relations =====
    categories = relationship(
        "Category",
        secondary=product_categories,
        back_populates="products"
    )
    
    images = relationship(
        "ProductImage",
        back_populates="product",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    cart_items = relationship(
        "CartItem",
        back_populates="product",
        cascade="all, delete-orphan"
    )
    
    order_items = relationship(
        "OrderItem",
        back_populates="product"
    )
    
    reviews = relationship(
        "Review",
        back_populates="product",
        cascade="all, delete-orphan"
    )
    
    # ===== Propriétés calculées =====
    @property
    def current_price(self) -> float:
        """Prix actuel (promo si disponible, sinon prix normal)"""
        if self.sale_price is not None and self.sale_price > 0:
            return float(self.sale_price)
        return float(self.price)
    
    @property
    def has_discount(self) -> bool:
        """Vérifie si le produit est en promotion"""
        return self.sale_price is not None and self.sale_price > 0
    
    @property
    def discount_percentage(self) -> Optional[float]:
        """Calcule le pourcentage de réduction"""
        if not self.has_discount:
            return None
        return round(((float(self.price) - float(self.sale_price)) / float(self.price)) * 100, 2)
    
    @property
    def is_in_stock(self) -> bool:
        """Vérifie si le produit est en stock"""
        return self.stock > 0
    
    @property
    def main_image(self) -> Optional["ProductImage"]:
        """Retourne l'image principale du produit"""
        if not self.images:
            return None
        for image in self.images:
            if image.is_main:
                return image
        return self.images[0] if self.images else None
    
    @property
    def average_rating(self) -> Optional[float]:
        """Calcule la note moyenne des avis"""
        if not self.reviews:
            return None
        approved_reviews = [r for r in self.reviews if r.is_approved]
        if not approved_reviews:
            return None
        total = sum(r.rating for r in approved_reviews)
        return round(total / len(approved_reviews), 2)
    
    @property
    def review_count(self) -> int:
        """Nombre d'avis approuvés"""
        if not self.reviews:
            return 0
        return len([r for r in self.reviews if r.is_approved])
    
    def __repr__(self) -> str:
        return f"<Product(id={self.id}, name='{self.name}', price={self.current_price})>"


class ProductImage(Base):
    """
    Modèle ProductImage - Images des produits
    
    Relations:
        - product: Produit associé (N-1)
    """
    
    __tablename__ = "product_images"
    
    # ===== Colonnes =====
    id = Column(
        BigInteger().with_variant(BigInteger, "sqlite"),
        primary_key=True,
        autoincrement=True,
        comment="Identifiant unique"
    )
    
    product_id = Column(
        BigInteger,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Identifiant du produit"
    )
    
    image_url = Column(
        String(255),
        nullable=False,
        comment="URL de l'image"
    )
    
    is_main = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Image principale du produit"
    )
    
    created_at = Column(
        DateTime,
        default=func.now(),
        nullable=False,
        comment="Date d'ajout"
    )
    
    # ===== Relations =====
    product = relationship(
        "Product",
        back_populates="images"
    )
    
    def __repr__(self) -> str:
        return f"<ProductImage(id={self.id}, product_id={self.product_id}, is_main={self.is_main})>"