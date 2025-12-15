
"""
Modèle Review - Avis clients
"""

from sqlalchemy import (
    Column, BigInteger, Integer, Text, Boolean, ForeignKey, DateTime,
    func, CheckConstraint
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class Review(Base):
    """
    Modèle Review - Avis clients sur les produits
    
    Relations:
        - product: Produit évalué (N-1)
        - user: Auteur de l'avis (N-1)
    """
    
    __tablename__ = "reviews"
    
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
    
    user_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Identifiant de l'utilisateur"
    )
    
    rating = Column(
        Integer,
        nullable=False,
        comment="Note de 1 à 5 étoiles"
    )
    
    comment = Column(
        Text,
        nullable=True,
        comment="Commentaire textuel"
    )
    
    is_approved = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Avis approuvé par un modérateur"
    )
    
    created_at = Column(
        DateTime,
        default=func.now(),
        nullable=False,
        comment="Date de publication"
    )
    
    # ===== Contraintes =====
    __table_args__ = (
        CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
    )
    
    # ===== Relations =====
    product = relationship(
        "Product",
        back_populates="reviews"
    )
    
    user = relationship(
        "User",
        back_populates="reviews"
    )
    
    # ===== Propriétés calculées =====
    @property
    def has_comment(self) -> bool:
        """Vérifie si l'avis contient un commentaire"""
        return self.comment is not None and len(self.comment.strip()) > 0
    
    @property
    def rating_stars(self) -> str:
        """Retourne la note sous forme d'étoiles"""
        return "★" * self.rating + "☆" * (5 - self.rating)
    
    def __repr__(self) -> str:
        return f"<Review(id={self.id}, product_id={self.product_id}, user_id={self.user_id}, rating={self.rating})>"