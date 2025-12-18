"""
Dépendances communes pour les routes API
Authentification, pagination, etc.
"""

from typing import Optional, Annotated
from fastapi import Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, RoleChecker
from app.models.user import User, UserRole


# ===== Dépendances de base =====

# Session de base de données
DatabaseDep = Annotated[AsyncSession, Depends(get_db)]

# Utilisateur actuel
CurrentUser = Annotated[User, Depends(get_current_user)]


# ===== Dépendances de rôles =====

# Vérifier que l'utilisateur est admin
async def require_admin(current_user: CurrentUser) -> User:
    """Vérifie que l'utilisateur est admin"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissions administrateur requises"
        )
    return current_user

AdminUser = Annotated[User, Depends(require_admin)]


# Vérifier que l'utilisateur est admin ou manager
async def require_admin_or_manager(current_user: CurrentUser) -> User:
    """Vérifie que l'utilisateur est admin ou manager"""
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissions administrateur ou manager requises"
        )
    return current_user

StaffUser = Annotated[User, Depends(require_admin_or_manager)]


# ===== Dépendances de pagination =====

class PaginationParams:
    """Paramètres de pagination communs"""
    
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Numéro de page"),
        page_size: int = Query(20, ge=1, le=100, description="Taille de page")
    ):
        self.page = page
        self.page_size = page_size
    
    @property
    def skip(self) -> int:
        """Calcule l'offset"""
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        """Retourne la limite"""
        return self.page_size
    
    def get_total_pages(self, total: int) -> int:
        """Calcule le nombre total de pages"""
        return (total + self.page_size - 1) // self.page_size


PaginationDep = Annotated[PaginationParams, Depends()]


# ===== Dépendances de tri =====

class SortParams:
    """Paramètres de tri communs"""
    
    def __init__(
        self,
        sort_by: Optional[str] = Query(
            "created_at",
            description="Champ de tri"
        ),
        sort_order: str = Query(
            "desc",
            regex="^(asc|desc)$",
            description="Ordre de tri (asc/desc)"
        )
    ):
        self.sort_by = sort_by
        self.sort_order = sort_order
    
    @property
    def is_ascending(self) -> bool:
        """Vérifie si le tri est ascendant"""
        return self.sort_order.lower() == "asc"
    
    @property
    def is_descending(self) -> bool:
        """Vérifie si le tri est descendant"""
        return self.sort_order.lower() == "desc"


SortDep = Annotated[SortParams, Depends()]


# ===== Dépendances de recherche =====

class SearchParams:
    """Paramètres de recherche communs"""
    
    def __init__(
        self,
        q: Optional[str] = Query(
            None,
            min_length=2,
            max_length=100,
            description="Terme de recherche"
        )
    ):
        self.query = q
    
    @property
    def has_query(self) -> bool:
        """Vérifie si une recherche est demandée"""
        return self.query is not None and len(self.query.strip()) > 0
    
    @property
    def clean_query(self) -> Optional[str]:
        """Retourne la requête nettoyée"""
        if not self.has_query:
            return None
        return self.query.strip()


SearchDep = Annotated[SearchParams, Depends()]


# ===== Dépendances combinées =====

class CommonQueryParams:
    """Paramètres de requête communs (pagination + tri + recherche)"""
    
    def __init__(
        self,
        pagination: PaginationDep,
        sort: SortDep,
        search: SearchDep
    ):
        self.pagination = pagination
        self.sort = sort
        self.search = search


CommonParams = Annotated[CommonQueryParams, Depends()]


# ===== Helpers pour réponses paginées =====

def create_paginated_response(
    items: list,
    total: int,
    page: int,
    page_size: int
) -> dict:
    """
    Crée une réponse paginée standardisée
    
    Args:
        items: Liste d'items
        total: Nombre total d'items
        page: Numéro de page actuelle
        page_size: Taille de page
    
    Returns:
        Dict avec pagination
    """
    total_pages = (total + page_size - 1) // page_size
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }