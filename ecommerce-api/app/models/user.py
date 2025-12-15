"""
Modèle User - Utilisateurs et clients
"""

from sqlalchemy import (
    Column, BigInteger, String, Boolean, DateTime, Enum
)
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel


class UserRole(str, enum.Enum):
    """Rôles utilisateur"""
    CUSTOMER = "customer"
    ADMIN = "admin"
    MANAGER = "manager"


class User(BaseModel):
    """
    Modèle User - Gestion des utilisateurs
    
    Relations:
        - addresses: Liste des adresses (1-N)
        - carts: Paniers de l'utilisateur (1-N)
        - orders: Commandes de l'utilisateur (1-N)
        - reviews: Avis laissés par l'utilisateur (1-N)
        - activity_logs: Logs d'activité (1-N)
    """
    
    __tablename__ = "users"
    
    # ===== Colonnes =====
    id = Column(
        BigInteger().with_variant(BigInteger, "sqlite"),
        primary_key=True,
        autoincrement=True,
        comment="Identifiant unique"
    )
    
    role = Column(
        Enum(UserRole),
        default=UserRole.CUSTOMER,
        nullable=False,
        comment="Rôle de l'utilisateur"
    )
    
    first_name = Column(
        String(100),
        nullable=False,
        comment="Prénom"
    )
    
    last_name = Column(
        String(100),
        nullable=False,
        comment="Nom de famille"
    )
    
    email = Column(
        String(191),
        unique=True,
        nullable=False,
        index=True,
        comment="Email (identifiant de connexion)"
    )
    
    password_hash = Column(
        String(255),
        nullable=False,
        comment="Hash du mot de passe (bcrypt)"
    )
    
    phone = Column(
        String(30),
        nullable=True,
        comment="Numéro de téléphone"
    )
    
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Compte actif ou désactivé"
    )
    
    email_verified_at = Column(
        DateTime,
        nullable=True,
        comment="Date de vérification de l'email"
    )
    
    # ===== Relations =====
    addresses = relationship(
        "Address",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    carts = relationship(
        "Cart",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    orders = relationship(
        "Order",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    reviews = relationship(
        "Review",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    activity_logs = relationship(
        "ActivityLog",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    # ===== Propriétés calculées =====
    @property
    def full_name(self) -> str:
        """Nom complet de l'utilisateur"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_admin(self) -> bool:
        """Vérifie si l'utilisateur est admin"""
        return self.role == UserRole.ADMIN
    
    @property
    def is_manager(self) -> bool:
        """Vérifie si l'utilisateur est manager"""
        return self.role == UserRole.MANAGER
    
    @property
    def is_customer(self) -> bool:
        """Vérifie si l'utilisateur est client"""
        return self.role == UserRole.CUSTOMER
    
    @property
    def is_email_verified(self) -> bool:
        """Vérifie si l'email est vérifié"""
        return self.email_verified_at is not None
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"