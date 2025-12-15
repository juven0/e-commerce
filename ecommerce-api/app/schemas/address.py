
"""
Schemas Pydantic pour Address
Validation et sérialisation des adresses
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from app.models.address import AddressType


# ===== Schemas de base =====
class AddressBase(BaseModel):
    """Schema de base pour Address"""
    type: AddressType = Field(..., description="Type d'adresse")
    full_name: Optional[str] = Field(None, max_length=200, description="Nom complet du destinataire")
    address_line1: str = Field(..., min_length=1, max_length=255, description="Adresse ligne 1")
    address_line2: Optional[str] = Field(None, max_length=255, description="Complément d'adresse")
    city: str = Field(..., min_length=1, max_length=100, description="Ville")
    state: Optional[str] = Field(None, max_length=100, description="État/Province/Région")
    postal_code: Optional[str] = Field(None, max_length=20, description="Code postal")
    country: str = Field(..., min_length=1, max_length=100, description="Pays")
    phone: Optional[str] = Field(None, max_length=30, description="Téléphone")


# ===== Schemas de création =====
class AddressCreate(AddressBase):
    """Schema pour créer une adresse"""
    pass


# ===== Schemas de mise à jour =====
class AddressUpdate(BaseModel):
    """Schema pour mettre à jour une adresse"""
    type: Optional[AddressType] = None
    full_name: Optional[str] = Field(None, max_length=200)
    address_line1: Optional[str] = Field(None, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=30)


# ===== Schemas de réponse =====
class AddressResponse(AddressBase):
    """Schema de réponse pour une adresse"""
    id: int
    user_id: int
    created_at: datetime
    
    model_config = {
        "from_attributes": True
    }


class AddressListResponse(BaseModel):
    """Schema de réponse pour liste d'adresses"""
    addresses: list[AddressResponse]
    total: int