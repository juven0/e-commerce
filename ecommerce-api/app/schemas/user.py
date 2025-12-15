
"""
Schemas Pydantic pour User
Validation et sérialisation des données utilisateur
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime

from app.models.user import UserRole


# ===== Schemas de base =====
class UserBase(BaseModel):
    """Schema de base pour User"""
    email: EmailStr = Field(..., description="Adresse email")
    first_name: str = Field(..., min_length=1, max_length=100, description="Prénom")
    last_name: str = Field(..., min_length=1, max_length=100, description="Nom de famille")
    phone: Optional[str] = Field(None, max_length=30, description="Téléphone")


# ===== Schemas de création =====
class UserCreate(UserBase):
    """Schema pour créer un utilisateur"""
    password: str = Field(..., min_length=8, max_length=100, description="Mot de passe")
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Valide la force du mot de passe"""
        if len(v) < 8:
            raise ValueError("Le mot de passe doit contenir au moins 8 caractères")
        if not any(c.isupper() for c in v):
            raise ValueError("Le mot de passe doit contenir au moins une majuscule")
        if not any(c.islower() for c in v):
            raise ValueError("Le mot de passe doit contenir au moins une minuscule")
        if not any(c.isdigit() for c in v):
            raise ValueError("Le mot de passe doit contenir au moins un chiffre")
        return v


class UserRegister(UserCreate):
    """Schema pour l'inscription utilisateur (alias de UserCreate)"""
    pass


# ===== Schemas de mise à jour =====
class UserUpdate(BaseModel):
    """Schema pour mettre à jour un utilisateur"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=30)
    email: Optional[EmailStr] = None


class UserUpdatePassword(BaseModel):
    """Schema pour changer le mot de passe"""
    current_password: str = Field(..., description="Mot de passe actuel")
    new_password: str = Field(..., min_length=8, description="Nouveau mot de passe")
    
    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Valide la force du nouveau mot de passe"""
        if len(v) < 8:
            raise ValueError("Le mot de passe doit contenir au moins 8 caractères")
        if not any(c.isupper() for c in v):
            raise ValueError("Le mot de passe doit contenir au moins une majuscule")
        if not any(c.islower() for c in v):
            raise ValueError("Le mot de passe doit contenir au moins une minuscule")
        if not any(c.isdigit() for c in v):
            raise ValueError("Le mot de passe doit contenir au moins un chiffre")
        return v


class UserUpdateRole(BaseModel):
    """Schema pour mettre à jour le rôle (admin uniquement)"""
    role: UserRole = Field(..., description="Nouveau rôle")


class UserUpdateStatus(BaseModel):
    """Schema pour activer/désactiver un compte (admin uniquement)"""
    is_active: bool = Field(..., description="Statut du compte")


# ===== Schemas de réponse =====
class UserResponse(UserBase):
    """Schema de réponse pour un utilisateur"""
    id: int
    role: UserRole
    is_active: bool
    email_verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = {
        "from_attributes": True
    }


class UserPublicResponse(BaseModel):
    """Schema de réponse publique (informations limitées)"""
    id: int
    first_name: str
    last_name: str
    
    model_config = {
        "from_attributes": True
    }
    
    @property
    def full_name(self) -> str:
        """Nom complet"""
        return f"{self.first_name} {self.last_name}"


class UserProfileResponse(UserResponse):
    """Schema de réponse pour le profil utilisateur complet"""
    
    @property
    def full_name(self) -> str:
        """Nom complet"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_email_verified(self) -> bool:
        """Vérifie si l'email est vérifié"""
        return self.email_verified_at is not None


# ===== Schemas de liste =====
class UserListResponse(BaseModel):
    """Schema de réponse pour liste d'utilisateurs (admin)"""
    users: list[UserResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ===== Schemas pour vérification email =====
class EmailVerificationRequest(BaseModel):
    """Schema pour demander une vérification d'email"""
    email: EmailStr = Field(..., description="Email à vérifier")


class EmailVerificationConfirm(BaseModel):
    """Schema pour confirmer la vérification d'email"""
    token: str = Field(..., description="Token de vérification")


# ===== Schemas pour réinitialisation mot de passe =====
class PasswordResetRequest(BaseModel):
    """Schema pour demander une réinitialisation de mot de passe"""
    email: EmailStr = Field(..., description="Email du compte")


class PasswordResetConfirm(BaseModel):
    """Schema pour confirmer la réinitialisation"""
    token: str = Field(..., description="Token de réinitialisation")
    new_password: str = Field(..., min_length=8, description="Nouveau mot de passe")
    
    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Valide la force du nouveau mot de passe"""
        if len(v) < 8:
            raise ValueError("Le mot de passe doit contenir au moins 8 caractères")
        if not any(c.isupper() for c in v):
            raise ValueError("Le mot de passe doit contenir au moins une majuscule")
        if not any(c.islower() for c in v):
            raise ValueError("Le mot de passe doit contenir au moins une minuscule")
        if not any(c.isdigit() for c in v):
            raise ValueError("Le mot de passe doit contenir au moins un chiffre")
        return v