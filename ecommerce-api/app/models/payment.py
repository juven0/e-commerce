
"""
Modèle Payment - Paiements
"""

from sqlalchemy import (
    Column, BigInteger, DECIMAL, Enum, String, DateTime, ForeignKey, func
)
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class PaymentMethod(str, enum.Enum):
    """Méthodes de paiement"""
    CARD = "card"
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"
    CASH_ON_DELIVERY = "cash_on_delivery"


class PaymentStatus(str, enum.Enum):
    """Statuts de paiement"""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"


class Payment(Base):
    """
    Modèle Payment - Paiements
    
    Relations:
        - order: Commande associée (N-1)
    """
    
    __tablename__ = "payments"
    
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
    
    method = Column(
        Enum(PaymentMethod),
        nullable=False,
        comment="Méthode de paiement"
    )
    
    status = Column(
        Enum(PaymentStatus),
        default=PaymentStatus.PENDING,
        nullable=False,
        index=True,
        comment="Statut du paiement"
    )
    
    amount = Column(
        DECIMAL(12, 2),
        nullable=False,
        comment="Montant payé"
    )
    
    transaction_reference = Column(
        String(191),
        nullable=True,
        unique=True,
        index=True,
        comment="Référence de transaction (ex: Stripe payment_intent_id)"
    )
    
    paid_at = Column(
        DateTime,
        nullable=True,
        comment="Date effective du paiement"
    )
    
    created_at = Column(
        DateTime,
        default=func.now(),
        nullable=False,
        comment="Date de création"
    )
    
    # ===== Relations =====
    order = relationship(
        "Order",
        back_populates="payments"
    )
    
    # ===== Propriétés calculées =====
    @property
    def is_successful(self) -> bool:
        """Vérifie si le paiement a réussi"""
        return self.status == PaymentStatus.SUCCESS
    
    @property
    def is_pending(self) -> bool:
        """Vérifie si le paiement est en attente"""
        return self.status == PaymentStatus.PENDING
    
    @property
    def is_failed(self) -> bool:
        """Vérifie si le paiement a échoué"""
        return self.status == PaymentStatus.FAILED
    
    @property
    def is_refunded(self) -> bool:
        """Vérifie si le paiement a été remboursé"""
        return self.status == PaymentStatus.REFUNDED
    
    @property
    def can_be_refunded(self) -> bool:
        """Vérifie si le paiement peut être remboursé"""
        return self.status == PaymentStatus.SUCCESS
    
    def __repr__(self) -> str:
        return f"<Payment(id={self.id}, order_id={self.order_id}, method='{self.method}', status='{self.status}', amount={self.amount})>"