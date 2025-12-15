
"""
Schemas Pydantic pour Payment
Validation et sérialisation des paiements
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal

from app.models.payment import PaymentMethod, PaymentStatus


# ===== Schemas de base =====
class PaymentBase(BaseModel):
    """Schema de base pour Payment"""
    method: PaymentMethod = Field(..., description="Méthode de paiement")
    amount: Decimal = Field(..., gt=0, description="Montant")


# ===== Schemas de création =====
class PaymentCreate(PaymentBase):
    """Schema pour créer un paiement"""
    order_id: int = Field(..., description="ID de la commande")


class PaymentInitiate(BaseModel):
    """Schema pour initier un paiement"""
    order_id: int = Field(..., description="ID de la commande")
    method: PaymentMethod = Field(..., description="Méthode de paiement")
    return_url: Optional[str] = Field(None, description="URL de retour après paiement")


# ===== Schemas de réponse =====
class PaymentResponse(BaseModel):
    """Schema de réponse pour un paiement"""
    id: int
    order_id: int
    method: PaymentMethod
    status: PaymentStatus
    amount: Decimal
    transaction_reference: Optional[str] = None
    paid_at: Optional[datetime] = None
    created_at: datetime
    
    model_config = {
        "from_attributes": True
    }


class PaymentDetailResponse(PaymentResponse):
    """Schema de réponse détaillé"""
    order: Optional["OrderResponse"] = None
    
    model_config = {
        "from_attributes": True
    }


# ===== Schemas pour webhooks =====
class StripeWebhookEvent(BaseModel):
    """Schema pour webhook Stripe"""
    id: str
    type: str
    data: dict


class PaypalWebhookEvent(BaseModel):
    """Schema pour webhook PayPal"""
    event_type: str
    resource: dict


# ===== Schemas de confirmation =====
class PaymentConfirmation(BaseModel):
    """Confirmation de paiement"""
    payment_id: int
    transaction_reference: str
    status: PaymentStatus


class PaymentSuccessResponse(BaseModel):
    """Réponse après paiement réussi"""
    payment: PaymentResponse
    message: str = "Paiement effectué avec succès"
    success: bool = True


class PaymentFailedResponse(BaseModel):
    """Réponse après échec de paiement"""
    message: str = "Le paiement a échoué"
    success: bool = False
    error_code: Optional[str] = None
    error_message: Optional[str] = None


# ===== Schemas pour Stripe =====
class StripePaymentIntent(BaseModel):
    """Intent de paiement Stripe"""
    client_secret: str = Field(..., description="Client secret pour Stripe")
    payment_intent_id: str = Field(..., description="ID du payment intent")
    amount: Decimal
    currency: str = "eur"


class StripeCheckoutSession(BaseModel):
    """Session de checkout Stripe"""
    session_id: str
    url: str
    order_id: int


# ===== Schemas pour PayPal =====
class PayPalOrderCreate(BaseModel):
    """Création d'ordre PayPal"""
    order_id: str = Field(..., description="ID de l'ordre PayPal")
    approval_url: str = Field(..., description="URL d'approbation")


class PayPalOrderCapture(BaseModel):
    """Capture d'ordre PayPal"""
    paypal_order_id: str = Field(..., description="ID ordre PayPal")


# ===== Schemas pour remboursement =====
class RefundRequest(BaseModel):
    """Demande de remboursement"""
    payment_id: int = Field(..., description="ID du paiement")
    amount: Optional[Decimal] = Field(None, description="Montant (partiel si spécifié)")
    reason: Optional[str] = Field(None, description="Raison du remboursement")


class RefundResponse(BaseModel):
    """Réponse après remboursement"""
    payment_id: int
    refund_amount: Decimal
    status: PaymentStatus
    message: str = "Remboursement effectué"
    success: bool = True


# ===== Schemas de liste =====
class PaymentListResponse(BaseModel):
    """Liste de paiements"""
    payments: list[PaymentResponse]
    total: int
    page: int
    page_size: int


# Import pour résoudre les références forward
from app.schemas.order import OrderResponse

PaymentDetailResponse.model_rebuild()