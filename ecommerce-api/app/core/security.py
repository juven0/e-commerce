
"""
Sécurité & Authentification
Gestion JWT, hashing passwords, OAuth2
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db


# ===== Configuration du hashing des mots de passe =====
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=settings.BCRYPT_ROUNDS
)


# ===== OAuth2 Schema =====
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/login"
)


# ===== Fonctions de hashing =====
def hash_password(password: str) -> str:
    """
    Hash un mot de passe avec bcrypt
    
    Args:
        password: Mot de passe en clair
    
    Returns:
        Hash du mot de passe
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifie qu'un mot de passe correspond à son hash
    
    Args:
        plain_password: Mot de passe en clair
        hashed_password: Hash à vérifier
    
    Returns:
        True si le mot de passe est correct
    """
    return pwd_context.verify(plain_password, hashed_password)


# ===== Fonctions JWT =====
def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Crée un token JWT d'accès
    
    Args:
        data: Données à encoder dans le token (user_id, email, role, etc.)
        expires_delta: Durée de validité personnalisée
    
    Returns:
        Token JWT encodé
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def create_refresh_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Crée un token JWT de rafraîchissement
    
    Args:
        data: Données à encoder (généralement juste user_id)
        expires_delta: Durée de validité personnalisée
    
    Returns:
        Token JWT encodé
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    Décode et valide un token JWT
    
    Args:
        token: Token JWT à décoder
    
    Returns:
        Payload du token
    
    Raises:
        HTTPException: Si le token est invalide ou expiré
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )


def create_email_verification_token(email: str) -> str:
    """
    Crée un token de vérification d'email
    
    Args:
        email: Email à vérifier
    
    Returns:
        Token de vérification
    """
    data = {"sub": email, "type": "email_verification"}
    expires = timedelta(hours=24)
    return create_access_token(data, expires)


def create_password_reset_token(email: str) -> str:
    """
    Crée un token de réinitialisation de mot de passe
    
    Args:
        email: Email de l'utilisateur
    
    Returns:
        Token de réinitialisation
    """
    data = {"sub": email, "type": "password_reset"}
    expires = timedelta(hours=1)
    return create_access_token(data, expires)


# ===== Dependency pour récupérer l'utilisateur courant =====
async def get_current_user_id(
    token: str = Depends(oauth2_scheme)
) -> int:
    """
    Extrait l'ID de l'utilisateur depuis le token JWT
    
    Args:
        token: Token JWT depuis le header Authorization
    
    Returns:
        ID de l'utilisateur
    
    Raises:
        HTTPException: Si le token est invalide
    """
    payload = decode_token(token)
    
    # Vérifier le type de token
    token_type = payload.get("type")
    if token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Type de token invalide",
        )
    
    user_id: Optional[int] = payload.get("sub")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide: utilisateur non trouvé",
        )
    
    return int(user_id)


async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupère l'utilisateur complet depuis la base de données
    
    Args:
        user_id: ID de l'utilisateur depuis le token
        db: Session de base de données
    
    Returns:
        Modèle User complet
    
    Raises:
        HTTPException: Si l'utilisateur n'existe pas ou est inactif
    """
    from app.repositories.user import UserRepository
    
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte utilisateur désactivé"
        )
    
    return user


async def get_current_active_user(
    current_user = Depends(get_current_user)
):
    """
    Alias pour get_current_user (pour clarté du code)
    Vérifie que l'utilisateur est actif
    """
    return current_user


# ===== Vérification des rôles =====
class RoleChecker:
    """
    Classe pour vérifier les rôles utilisateur
    
    Usage:
        @app.get("/admin", dependencies=[Depends(RoleChecker(["admin"]))])
    """
    
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles
    
    async def __call__(self, current_user = Depends(get_current_user)):
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissions insuffisantes"
            )
        return current_user


# Instances pré-configurées pour faciliter l'usage
require_admin = RoleChecker(["admin"])
require_admin_or_manager = RoleChecker(["admin", "manager"])


# ===== Utilitaires de sécurité =====
def generate_random_token(length: int = 32) -> str:
    """
    Génère un token aléatoire sécurisé
    Utile pour les tokens de vérification, reset password, etc.
    
    Args:
        length: Longueur du token
    
    Returns:
        Token aléatoire en hexadécimal
    """
    import secrets
    return secrets.token_urlsafe(length)


def mask_email(email: str) -> str:
    """
    Masque partiellement un email pour la confidentialité
    
    Example:
        john.doe@example.com -> j***@example.com
    """
    if "@" not in email:
        return email
    
    local, domain = email.split("@")
    if len(local) <= 2:
        masked_local = local[0] + "*"
    else:
        masked_local = local[0] + "***"
    
    return f"{masked_local}@{domain}"


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Valide la force d'un mot de passe
    
    Returns:
        (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Le mot de passe doit contenir au moins 8 caractères"
    
    if not any(c.isupper() for c in password):
        return False, "Le mot de passe doit contenir au moins une majuscule"
    
    if not any(c.islower() for c in password):
        return False, "Le mot de passe doit contenir au moins une minuscule"
    
    if not any(c.isdigit() for c in password):
        return False, "Le mot de passe doit contenir au moins un chiffre"
    
    return True, ""