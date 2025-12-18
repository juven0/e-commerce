
"""
Routes API - Utilisateurs
Gestion des utilisateurs (profil, CRUD admin)
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, status, Query

from app.api.dependencies import (
    DatabaseDep,
    CurrentUser,
    AdminUser,
    PaginationDep,
    SearchDep,
    create_paginated_response
)
from app.schemas.user import (
    UserUpdate,
    UserResponse,
    UserProfileResponse,
    UserUpdateRole,
    UserUpdateStatus
)
from app.models.user import UserRole
from app.services.user import UserService


router = APIRouter(prefix="/users", tags=["Users"])


# ===== Routes publiques/utilisateur =====

@router.get(
    "/me",
    response_model=UserProfileResponse,
    summary="Mon profil"
)
async def get_my_profile(current_user: CurrentUser):
    """
    Récupère le profil de l'utilisateur connecté
    """
    return current_user


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Mettre à jour mon profil"
)
async def update_my_profile(
    user_update: UserUpdate,
    current_user: CurrentUser,
    db: DatabaseDep
):
    """
    Met à jour le profil de l'utilisateur connecté
    
    - Peut modifier: prénom, nom, téléphone, email
    - L'email doit être unique
    """
    user_service = UserService(db)
    
    updated_user = await user_service.update_user(
        current_user.id,
        user_update
    )
    
    return updated_user


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer mon compte"
)
async def delete_my_account(
    current_user: CurrentUser,
    db: DatabaseDep
):
    """
    Supprime le compte de l'utilisateur connecté
    
    ⚠️ Action irréversible
    """
    user_service = UserService(db)
    
    await user_service.delete_user(current_user.id)
    
    return None


# ===== Routes admin =====

@router.get(
    "",
    response_model=dict,
    summary="Liste des utilisateurs (Admin)"
)
async def get_users(
    pagination: PaginationDep,
    search: SearchDep,
    role: Optional[UserRole] = Query(None, description="Filtrer par rôle"),
    is_active: Optional[bool] = Query(None, description="Filtrer par statut"),
    admin_user: AdminUser = None,
    db: DatabaseDep = None
):
    """
    Récupère la liste des utilisateurs avec filtres et pagination
    
    **Réservé aux administrateurs**
    
    - Pagination
    - Recherche par nom/email
    - Filtrage par rôle et statut
    """
    user_service = UserService(db)
    
    # Recherche
    if search.has_query:
        users, total = await user_service.search_users(
            search.clean_query,
            pagination.skip,
            pagination.limit
        )
    # Filtrage par rôle
    elif role:
        users, total = await user_service.get_users_by_role(
            role,
            pagination.skip,
            pagination.limit
        )
    # Tous les utilisateurs
    else:
        users, total = await user_service.get_all_users(
            pagination.skip,
            pagination.limit,
            active_only=is_active if is_active is not None else False
        )
    
    return create_paginated_response(
        items=[UserResponse.model_validate(u) for u in users],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size
    )


@router.get(
    "/statistics",
    response_model=dict,
    summary="Statistiques utilisateurs (Admin)"
)
async def get_user_statistics(
    admin_user: AdminUser,
    db: DatabaseDep
):
    """
    Récupère les statistiques des utilisateurs
    
    **Réservé aux administrateurs**
    """
    user_service = UserService(db)
    
    stats = await user_service.get_user_statistics()
    
    return stats


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Détails d'un utilisateur (Admin)"
)
async def get_user_by_id(
    user_id: int,
    admin_user: AdminUser,
    db: DatabaseDep
):
    """
    Récupère les détails d'un utilisateur par son ID
    
    **Réservé aux administrateurs**
    """
    user_service = UserService(db)
    
    user = await user_service.get_user_by_id(user_id)
    
    return user


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Mettre à jour un utilisateur (Admin)"
)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    admin_user: AdminUser,
    db: DatabaseDep
):
    """
    Met à jour un utilisateur
    
    **Réservé aux administrateurs**
    """
    user_service = UserService(db)
    
    updated_user = await user_service.update_user(user_id, user_update)
    
    return updated_user


@router.patch(
    "/{user_id}/role",
    response_model=UserResponse,
    summary="Changer le rôle (Admin)"
)
async def update_user_role(
    user_id: int,
    role_update: UserUpdateRole,
    admin_user: AdminUser,
    db: DatabaseDep
):
    """
    Change le rôle d'un utilisateur
    
    **Réservé aux administrateurs**
    """
    user_service = UserService(db)
    
    updated_user = await user_service.update_user_role(user_id, role_update.role)
    
    return updated_user


@router.patch(
    "/{user_id}/activate",
    response_model=UserResponse,
    summary="Activer un utilisateur (Admin)"
)
async def activate_user(
    user_id: int,
    admin_user: AdminUser,
    db: DatabaseDep
):
    """
    Active un compte utilisateur
    
    **Réservé aux administrateurs**
    """
    user_service = UserService(db)
    
    activated_user = await user_service.activate_user(user_id)
    
    return activated_user


@router.patch(
    "/{user_id}/deactivate",
    response_model=UserResponse,
    summary="Désactiver un utilisateur (Admin)"
)
async def deactivate_user(
    user_id: int,
    admin_user: AdminUser,
    db: DatabaseDep
):
    """
    Désactive un compte utilisateur
    
    **Réservé aux administrateurs**
    """
    user_service = UserService(db)
    
    deactivated_user = await user_service.deactivate_user(user_id)
    
    return deactivated_user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer un utilisateur (Admin)"
)
async def delete_user(
    user_id: int,
    admin_user: AdminUser,
    db: DatabaseDep
):
    """
    Supprime un utilisateur
    
    **Réservé aux administrateurs**
    
    ⚠️ Action irréversible
    """
    user_service = UserService(db)
    
    await user_service.delete_user(user_id)
    
    return None