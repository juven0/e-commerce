
"""
Modèle Coupon - Coupons de réduction
"""

from sqlalchemy import (
    Column, BigInteger, String, DECIMAL, Enum, Boolean, DateTime, func
)
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

from app.core.database import Base


class DiscountType(str, enum.Enum):
    """Types de réduction"""
    PERCENTAGE = "percentage"
    FIXED = "fixed"


class Coupon(Base):
    """
    Modèle Coupon - Coupons de réduction
    
    Relations:
        - orders: Commandes utilisant ce coupon (N-N via order_coupons)
    """
    
    __tablename__ = "coupons"
    
    # ===== Colonnes =====
    id = Column(
        BigInteger().with_variant(BigInteger, "sqlite"),
        primary_key=True,
        autoincrement=True,
        comment="Identifiant unique"
    )
    
    code = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Code promo (ex: NOEL2024)"
    )
    
    discount_type = Column(
        Enum(DiscountType),
        nullable=False,
        comment="Type de réduction (pourcentage ou montant fixe)"
    )
    
    discount_value = Column(
        DECIMAL(10, 2),
        nullable=False,
        comment="Valeur de la réduction (ex: 20 pour 20% ou 20€)"
    )
    
    min_order_amount = Column(
        DECIMAL(10, 2),
        nullable=True,
        comment="Montant minimum de commande pour utiliser le coupon"
    )
    
    expires_at = Column(
        DateTime,
        nullable=True,
        comment="Date d'expiration du coupon"
    )
    
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Coupon actif ou désactivé"
    )
    
    created_at = Column(
        DateTime,
        default=func.now(),
        nullable=False,
        comment="Date de création"
    )
    
    # ===== Relations =====
    orders = relationship(
        "Order",
        secondary="order_coupons",
        back_populates="coupons"
    )
    
    # ===== Propriétés calculées =====
    @property
    def is_expired(self) -> bool:
        """Vérifie si le coupon est expiré"""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_valid(self) -> bool:
        """Vérifie si le coupon est valide (actif et non expiré)"""
        return self.is_active and not self.is_expired
    
    @property
    def is_percentage(self) -> bool:
        """Vérifie si c'est une réduction en pourcentage"""
        return self.discount_type == DiscountType.PERCENTAGE
    
    @property
    def is_fixed(self) -> bool:
        """Vérifie si c'est une réduction fixe"""
        return self.discount_type == DiscountType.FIXED
    
    def calculate_discount(self, order_amount: float) -> float:
        """
        Calcule le montant de la réduction pour un montant donné
        
        Args:
            order_amount: Montant de la commande
        
        Returns:
            Montant de la réduction
        """
        if not self.is_valid:
            return 0.0
        
        if self.min_order_amount and order_amount < float(self.min_order_amount):
            return 0.0
        
        if self.is_percentage:
            discount = order_amount * (float(self.discount_value) / 100)
            return min(discount, order_amount)  # Ne peut pas dépasser le montant
        
        # Fixed discount
        return min(float(self.discount_value), order_amount)
    
    def __repr__(self) -> str:
        discount_str = f"{self.discount_value}%" if self.is_percentage else f"{self.discount_value}€"
        return f"<Coupon(id={self.id}, code='{self.code}', discount={discount_str}, valid={self.is_valid})>"