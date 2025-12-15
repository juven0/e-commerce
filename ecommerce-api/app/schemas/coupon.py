
"""
Schemas Pydantic pour Coupon
Validation et sérialisation des coupons
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from decimal import Decimal

from app.models.coupon import DiscountType


# ===== Schemas de base =====
class CouponBase(BaseModel):
    """Schema de base pour Coupon"""
    code: str = Field(..., min_length=3, max_length=50, description="Code promo")
    discount_type: DiscountType = Field(..., description="Type de réduction")
    discount_value: Decimal = Field(..., gt=0, description="Valeur de réduction")
    min_order_amount: Optional[Decimal] = Field(None, ge=0, description="Montant minimum")
    expires_at: Optional[datetime] = Field(None, description="Date d'expiration")
    is_active: bool = Field(default=True, description="Coupon actif")
    
    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        """Normalise le code en majuscules"""
        return v.upper().strip()
    
    @field_validator("discount_value")
    @classmethod
    def validate_discount(cls, v: Decimal, info) -> Decimal:
        """Valide la valeur de réduction selon le type"""
        discount_type = info.data.get("discount_type")
        if discount_type == DiscountType.PERCENTAGE:
            if v > 100:
                raise ValueError("Le pourcentage de réduction ne peut pas dépasser 100%")
        return v


# ===== Schemas de création =====
class CouponCreate(CouponBase):
    """Schema pour créer un coupon"""
    pass


# ===== Schemas de mise à jour =====
class CouponUpdate(BaseModel):
    """Schema pour mettre à jour un coupon"""
    discount_type: Optional[DiscountType] = None
    discount_value: Optional[Decimal] = Field(None, gt=0)
    min_order_amount: Optional[Decimal] = Field(None, ge=0)
    expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None


# ===== Schemas de réponse =====
class CouponResponse(CouponBase):
    """Schema de réponse pour un coupon"""
    id: int
    created_at: datetime
    
    model_config = {
        "from_attributes": True
    }


class CouponDetailResponse(CouponResponse):
    """Schema de réponse détaillé"""
    usage_count: int = Field(default=0, description="Nombre d'utilisations")
    is_expired: bool = Field(..., description="Coupon expiré")
    is_valid: bool = Field(..., description="Coupon valide")
    
    model_config = {
        "from_attributes": True
    }


# ===== Schemas de validation =====
class CouponValidateRequest(BaseModel):
    """Demande de validation de coupon"""
    code: str = Field(..., description="Code promo à valider")
    order_amount: Decimal = Field(..., gt=0, description="Montant de la commande")


class CouponValidateResponse(BaseModel):
    """Réponse de validation"""
    valid: bool = Field(..., description="Coupon valide")
    coupon: Optional[CouponResponse] = None
    discount_amount: Decimal = Field(default=Decimal(0), description="Montant de réduction")
    final_amount: Decimal = Field(..., description="Montant final après réduction")
    message: Optional[str] = None
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "valid": True,
                "coupon": {
                    "id": 1,
                    "code": "NOEL2024",
                    "discount_type": "percentage",
                    "discount_value": 20
                },
                "discount_amount": 10.00,
                "final_amount": 40.00,
                "message": "Code promo appliqué avec succès"
            }
        }
    }


# ===== Schemas d'application =====
class CouponApplyRequest(BaseModel):
    """Appliquer un coupon à une commande"""
    order_id: int = Field(..., description="ID de la commande")
    coupon_code: str = Field(..., description="Code promo")


class CouponApplyResponse(BaseModel):
    """Réponse après application"""
    message: str = "Coupon appliqué"
    discount_amount: Decimal
    new_total: Decimal
    success: bool = True


# ===== Schemas de liste =====
class CouponListResponse(BaseModel):
    """Liste de coupons"""
    coupons: list[CouponResponse]
    total: int
    page: int
    page_size: int


# ===== Schemas pour filtrage =====
class CouponFilterParams(BaseModel):
    """Paramètres de filtrage des coupons"""
    is_active: Optional[bool] = Field(True, description="Coupons actifs uniquement")
    discount_type: Optional[DiscountType] = Field(None, description="Type de réduction")
    valid_only: Optional[bool] = Field(False, description="Coupons valides uniquement (non expirés)")


# ===== Schemas de statistiques =====
class CouponStats(BaseModel):
    """Statistiques d'utilisation d'un coupon"""
    coupon_id: int
    code: str
    total_uses: int
    total_discount_given: Decimal
    average_order_amount: Decimal