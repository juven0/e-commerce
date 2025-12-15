
"""
Modèle Address - Adresses de livraison et facturation
"""

from sqlalchemy import (
    Column, BigInteger, String, Enum, ForeignKey, DateTime, func
)
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class AddressType(str, enum.Enum):
    """Types d'adresse"""
    BILLING = "billing"
    SHIPPING = "shipping"


class Address(Base):
    """
    Modèle Address - Adresses de livraison et facturation
    
    Relations:
        - user: Propriétaire de l'adresse (N-1)
        - billing_orders: Commandes utilisant cette adresse de facturation (1-N)
        - shipping_orders: Commandes utilisant cette adresse de livraison (1-N)
    """
    
    __tablename__ = "addresses"
    
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
        comment="Identifiant de l'utilisateur"
    )
    
    type = Column(
        Enum(AddressType),
        nullable=False,
        comment="Type d'adresse (facturation ou livraison)"
    )
    
    full_name = Column(
        String(200),
        nullable=True,
        comment="Nom complet du destinataire"
    )
    
    address_line1 = Column(
        String(255),
        nullable=False,
        comment="Adresse ligne 1"
    )
    
    address_line2 = Column(
        String(255),
        nullable=True,
        comment="Adresse ligne 2 (complément)"
    )
    
    city = Column(
        String(100),
        nullable=False,
        comment="Ville"
    )
    
    state = Column(
        String(100),
        nullable=True,
        comment="État/Province/Région"
    )
    
    postal_code = Column(
        String(20),
        nullable=True,
        comment="Code postal"
    )
    
    country = Column(
        String(100),
        nullable=False,
        comment="Pays"
    )
    
    phone = Column(
        String(30),
        nullable=True,
        comment="Numéro de téléphone"
    )
    
    created_at = Column(
        DateTime,
        default=func.now(),
        nullable=False,
        comment="Date de création"
    )
    
    # ===== Relations =====
    user = relationship(
        "User",
        back_populates="addresses"
    )
    
    billing_orders = relationship(
        "Order",
        back_populates="billing_address",
        foreign_keys="Order.billing_address_id"
    )
    
    shipping_orders = relationship(
        "Order",
        back_populates="shipping_address",
        foreign_keys="Order.shipping_address_id"
    )
    
    # ===== Propriétés calculées =====
    @property
    def full_address(self) -> str:
        """Adresse complète formatée"""
        parts = [self.address_line1]
        
        if self.address_line2:
            parts.append(self.address_line2)
        
        parts.append(f"{self.postal_code} {self.city}")
        
        if self.state:
            parts.append(self.state)
        
        parts.append(self.country)
        
        return ", ".join(parts)
    
    @property
    def is_billing(self) -> bool:
        """Vérifie si c'est une adresse de facturation"""
        return self.type == AddressType.BILLING
    
    @property
    def is_shipping(self) -> bool:
        """Vérifie si c'est une adresse de livraison"""
        return self.type == AddressType.SHIPPING
    
    def __repr__(self) -> str:
        return f"<Address(id={self.id}, type='{self.type}', city='{self.city}')>"