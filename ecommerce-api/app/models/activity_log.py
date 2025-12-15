
"""
Modèle ActivityLog - Logs d'activité utilisateur
"""

from sqlalchemy import (
    Column, BigInteger, String, ForeignKey, DateTime, func
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class ActivityLog(Base):
    """
    Modèle ActivityLog - Logs d'activité des utilisateurs
    Pour audit et sécurité
    
    Relations:
        - user: Utilisateur ayant effectué l'action (N-1)
    """
    
    __tablename__ = "activity_logs"
    
    # ===== Colonnes =====
    id = Column(
        BigInteger().with_variant(BigInteger, "sqlite"),
        primary_key=True,
        autoincrement=True,
        comment="Identifiant unique"
    )
    
    user_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Identifiant de l'utilisateur (nullable pour actions anonymes)"
    )
    
    action = Column(
        String(191),
        nullable=False,
        index=True,
        comment="Action effectuée (ex: 'login', 'create_order', 'update_profile')"
    )
    
    ip_address = Column(
        String(45),
        nullable=True,
        comment="Adresse IP de l'utilisateur"
    )
    
    user_agent = Column(
        String(255),
        nullable=True,
        comment="User agent du navigateur"
    )
    
    created_at = Column(
        DateTime,
        default=func.now(),
        nullable=False,
        index=True,
        comment="Date et heure de l'action"
    )
    
    # ===== Relations =====
    user = relationship(
        "User",
        back_populates="activity_logs"
    )
    
    # ===== Propriétés calculées =====
    @property
    def is_authenticated(self) -> bool:
        """Vérifie si l'action était authentifiée"""
        return self.user_id is not None
    
    def __repr__(self) -> str:
        user_info = f"user_id={self.user_id}" if self.user_id else "anonymous"
        return f"<ActivityLog(id={self.id}, {user_info}, action='{self.action}')>"