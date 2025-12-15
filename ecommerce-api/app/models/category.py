"""
Modèle Category - Catégories de produits (hiérarchiques)
"""

from sqlalchemy import (
    Column, BigInteger, String, Text, Boolean, ForeignKey, DateTime, func
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class Category(Base):
    """
    Modèle Category - Catégories de produits
    Supporte les catégories hiérarchiques (parent/enfant)
    
    Relations:
        - parent: Catégorie parente (N-1)
        - children: Sous-catégories (1-N)
        - products: Produits de cette catégorie (N-N via product_categories)
    """
    
    __tablename__ = "categories"
    
    # ===== Colonnes =====
    id = Column(
        BigInteger().with_variant(BigInteger, "sqlite"),
        primary_key=True,
        autoincrement=True,
        comment="Identifiant unique"
    )
    
    parent_id = Column(
        BigInteger,
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Identifiant de la catégorie parente"
    )
    
    name = Column(
        String(150),
        nullable=False,
        comment="Nom de la catégorie"
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
        comment="Description de la catégorie"
    )
    
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Catégorie active ou désactivée"
    )
    
    created_at = Column(
        DateTime,
        default=func.now(),
        nullable=False,
        comment="Date de création"
    )
    
    # ===== Relations =====
    # Relation parent/enfant (self-referencing)
    parent = relationship(
        "Category",
        remote_side=[id],
        back_populates="children"
    )
    
    children = relationship(
        "Category",
        back_populates="parent",
        cascade="all, delete"
    )
    
    # Relation avec les produits (many-to-many)
    products = relationship(
        "Product",
        secondary="product_categories",
        back_populates="categories"
    )
    
    # ===== Propriétés calculées =====
    @property
    def is_root(self) -> bool:
        """Vérifie si c'est une catégorie racine (sans parent)"""
        return self.parent_id is None
    
    @property
    def has_children(self) -> bool:
        """Vérifie si la catégorie a des sous-catégories"""
        return len(self.children) > 0 if self.children else False
    
    @property
    def level(self) -> int:
        """
        Retourne le niveau de profondeur de la catégorie
        0 = racine, 1 = premier niveau, etc.
        """
        if self.is_root:
            return 0
        level = 0
        current = self
        while current.parent_id is not None:
            level += 1
            current = current.parent
            if level > 10:  # Protection contre boucle infinie
                break
        return level
    
    @property
    def full_path(self) -> str:
        """
        Retourne le chemin complet de la catégorie
        Ex: "Électronique > Smartphones > Samsung"
        """
        if self.is_root:
            return self.name
        
        path = [self.name]
        current = self
        while current.parent_id is not None:
            current = current.parent
            path.insert(0, current.name)
            if len(path) > 10:  # Protection
                break
        
        return " > ".join(path)
    
    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name='{self.name}', slug='{self.slug}')>"