
"""
Classe de base pour tous les modèles
Contient les colonnes communes (timestamps, etc.)
"""

from datetime import datetime
from sqlalchemy import Column, DateTime, func
from sqlalchemy.orm import declared_attr

from app.core.database import Base


class TimestampMixin:
    """
    Mixin pour ajouter automatiquement les colonnes created_at et updated_at
    """
    
    @declared_attr
    def created_at(cls):
        return Column(
            DateTime,
            default=func.now(),
            nullable=False,
            comment="Date de création"
        )
    
    @declared_attr
    def updated_at(cls):
        return Column(
            DateTime,
            default=func.now(),
            onupdate=func.now(),
            nullable=False,
            comment="Date de dernière modification"
        )


class BaseModel(Base, TimestampMixin):
    """
    Classe de base abstraite pour tous les modèles
    Hérite de Base (SQLAlchemy) et TimestampMixin
    """
    
    __abstract__ = True  # Cette classe n'est pas une table
    
    def to_dict(self) -> dict:
        """
        Convertit le modèle en dictionnaire
        Utile pour la sérialisation
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def __repr__(self) -> str:
        """
        Représentation string du modèle
        """
        attrs = []
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            attrs.append(f"{column.name}={value!r}")
        return f"{self.__class__.__name__}({', '.join(attrs)})"