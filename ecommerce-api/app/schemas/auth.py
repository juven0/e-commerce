
"""
Schemas Pydantic pour Authentication
Validation et sérialisation des données d'authentification
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional

from app.models.user import UserRole


# ===== Schemas de connexion =====
class LoginRequest(BaseModel):
    """Schema pour la connexion"""
    email: EmailStr = Field(..., description="Email de connexion")
    password: str = Field(..., description="Mot de passe")


class LoginResponse(BaseModel):
    """Schema de réponse après connexion"""
    access_token: str = Field(..., description="Token JWT d'accès")
    refresh_token: str = Field(..., description="Token JWT de rafraîchissement")
    token_type: str = Field(default="bearer", description="Type de token")
    expires_in: int = Field(..., description="Durée de validité en secondes")
    user: "UserInfo"
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800,
                "user": {
                    "id": 1,
                    "email": "john@example.com",
                    "first_name": "John",
                    "last_name": "Doe",
                    "role": "customer"
                }
            }
        }
    }


class UserInfo(BaseModel):
    """Informations utilisateur dans la réponse de connexion"""
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    role: UserRole
    is_active: bool
    is_email_verified: bool
    
    model_config = {
        "from_attributes": True
    }


# ===== Schemas de rafraîchissement de token =====
class RefreshTokenRequest(BaseModel):
    """Schema pour rafraîchir le token"""
    refresh_token: str = Field(..., description="Token de rafraîchissement")


class RefreshTokenResponse(BaseModel):
    """Schema de réponse après rafraîchissement"""
    access_token: str = Field(..., description="Nouveau token d'accès")
    token_type: str = Field(default="bearer", description="Type de token")
    expires_in: int = Field(..., description="Durée de validité en secondes")


# ===== Schemas de déconnexion =====
class LogoutResponse(BaseModel):
    """Schema de réponse après déconnexion"""
    message: str = Field(default="Déconnexion réussie")


# ===== Schemas de vérification de token =====
class TokenPayload(BaseModel):
    """Payload du token JWT"""
    sub: int = Field(..., description="User ID")
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    type: str = Field(..., description="Type de token (access/refresh)")
    exp: int = Field(..., description="Expiration timestamp")
    iat: int = Field(..., description="Issued at timestamp")


class TokenVerifyRequest(BaseModel):
    """Schema pour vérifier un token"""
    token: str = Field(..., description="Token à vérifier")


class TokenVerifyResponse(BaseModel):
    """Schema de réponse après vérification"""
    valid: bool = Field(..., description="Token valide ou non")
    payload: Optional[TokenPayload] = None
    error: Optional[str] = None


# ===== Schemas pour OAuth2 =====
class OAuth2PasswordRequestForm(BaseModel):
    """Schema pour OAuth2 password flow (compatible avec FastAPI)"""
    username: EmailStr = Field(..., description="Email (username)")
    password: str = Field(..., description="Mot de passe")
    scope: str = Field(default="", description="Scopes OAuth2")
    grant_type: str = Field(default="password", description="Type de grant")


# ===== Schemas de réponse d'erreur =====
class AuthErrorResponse(BaseModel):
    """Schema de réponse d'erreur d'authentification"""
    detail: str = Field(..., description="Message d'erreur")
    error_code: Optional[str] = None
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "detail": "Email ou mot de passe incorrect",
                "error_code": "INVALID_CREDENTIALS"
            }
        }
    }


# ===== Schemas de succès générique =====
class AuthSuccessResponse(BaseModel):
    """Schema de réponse de succès générique"""
    message: str
    success: bool = True
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Opération réussie",
                "success": True
            }
        }
    }