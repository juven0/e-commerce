
"""
Routes API - Commandes
Création et gestion des commandes
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, status, Query, BackgroundTasks

from app.api.dependencies import (
    DatabaseDep,
    CurrentUser,
    StaffUser,
    PaginationDep,
    create_paginated_response
)
from app.schemas.order import (
    OrderFromCart,
    OrderResponse,
    OrderDetailResponse,
    OrderUpdateStatus,
    OrderCreatedResponse
)
from app.models.order import OrderStatus
from app.services.order import OrderService
from app.services.email import EmailService


router = APIRouter(prefix="/orders", tags=["Orders"])


# ===== Routes utilisateur =====

@router.post(
    "",
    response_model=OrderCreatedResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer une commande"
)
async def create_order(
    order_data: OrderFromCart,
    background_tasks: BackgroundTasks,
    current_user: CurrentUser,
    db: DatabaseDep
):
    """
    Crée une commande depuis le panier
    
    - Convertit le panier en commande
    - Applique le coupon si fourni
    - Diminue le stock des produits
    - Vide le panier
    - Envoie un email de confirmation
    """
    order_service = OrderService(db)
    email_service = EmailService()
    
    order = await order_service.create_order_from_cart(
        current_user.id,
        order_data
    )
    
    # Envoyer l'email de confirmation en arrière-plan
    background_tasks.add_task(
        email_service.send_order_confirmation,
        current_user,
        order
    )
    
    return OrderCreatedResponse(
        order=order,
        message="Commande créée avec succès",
        payment_required=True
    )


@router.get(
    "",
    response_model=dict,
    summary="Mes commandes"
)
async def get_my_orders(
    pagination: PaginationDep,
    current_user: CurrentUser,
    db: DatabaseDep
):
    """
    Récupère les commandes de l'utilisateur connecté
    
    - Historique des commandes
    - Pagination
    """
    order_service = OrderService(db)
    
    orders, total = await order_service.get_user_orders(
        current_user.id,
        pagination.skip,
        pagination.limit
    )
    
    return create_paginated_response(
        items=[OrderResponse.model_validate(o) for o in orders],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size
    )


@router.get(
    "/{order_id}",
    response_model=OrderDetailResponse,
    summary="Détails d'une commande"
)
async def get_order(
    order_id: int,
    current_user: CurrentUser,
    db: DatabaseDep
):
    """
    Récupère les détails complets d'une commande
    
    - Informations de la commande
    - Articles commandés
    - Adresses de facturation et livraison
    - Paiements associés
    
    L'utilisateur ne peut accéder qu'à ses propres commandes
    """
    order_service = OrderService(db)
    
    order = await order_service.get_order_by_id(order_id, current_user.id)
    
    return order


@router.post(
    "/{order_id}/cancel",
    response_model=OrderResponse,
    summary="Annuler une commande"
)
async def cancel_order(
    order_id: int,
    background_tasks: BackgroundTasks,
    current_user: CurrentUser,
    db: DatabaseDep
):
    """
    Annule une commande
    
    - Restaure le stock des produits
    - Change le statut en "cancelled"
    - Envoie un email de confirmation
    
    Possible uniquement si statut = pending ou paid
    """
    order_service = OrderService(db)
    email_service = EmailService()
    
    cancelled_order = await order_service.cancel_order(order_id, current_user.id)
    
    # Envoyer l'email en arrière-plan
    background_tasks.add_task(
        email_service.send_order_cancelled,
        current_user,
        cancelled_order
    )
    
    return cancelled_order


# ===== Routes staff =====

@router.get(
    "/all/list",
    response_model=dict,
    summary="Toutes les commandes (Staff)"
)
async def get_all_orders(
    pagination: PaginationDep,
    status: Optional[OrderStatus] = Query(None, description="Filtrer par statut"),
    staff_user: StaffUser = None,
    db: DatabaseDep = None
):
    """
    Récupère toutes les commandes
    
    **Réservé au staff (admin/manager)**
    
    - Pagination
    - Filtrage par statut
    """
    order_service = OrderService(db)
    
    orders, total = await order_service.get_all_orders(
        pagination.skip,
        pagination.limit,
        status
    )
    
    return create_paginated_response(
        items=[OrderResponse.model_validate(o) for o in orders],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size
    )


@router.get(
    "/statistics/summary",
    response_model=dict,
    summary="Statistiques commandes (Staff)"
)
async def get_order_statistics(
    staff_user: StaffUser,
    db: DatabaseDep
):
    """
    Récupère les statistiques des commandes
    
    **Réservé au staff (admin/manager)**
    """
    order_service = OrderService(db)
    
    stats = await order_service.get_order_statistics()
    
    return stats


@router.get(
    "/admin/{order_id}",
    response_model=OrderDetailResponse,
    summary="Détails commande (Staff)"
)
async def get_order_admin(
    order_id: int,
    staff_user: StaffUser,
    db: DatabaseDep
):
    """
    Récupère les détails d'une commande (vue admin)
    
    **Réservé au staff (admin/manager)**
    """
    order_service = OrderService(db)
    
    order = await order_service.get_order_by_id(order_id)
    
    return order


@router.patch(
    "/{order_id}/status",
    response_model=OrderResponse,
    summary="Changer le statut (Staff)"
)
async def update_order_status(
    order_id: int,
    status_update: OrderUpdateStatus,
    background_tasks: BackgroundTasks,
    staff_user: StaffUser,
    db: DatabaseDep
):
    """
    Met à jour le statut d'une commande
    
    **Réservé au staff (admin/manager)**
    
    - Envoie un email selon le nouveau statut
    """
    order_service = OrderService(db)
    email_service = EmailService()
    
    order = await order_service.get_order_by_id(order_id)
    updated_order = await order_service.update_order_status(
        order_id,
        status_update.status
    )
    
    # Envoyer les emails appropriés
    user = order.user
    
    if status_update.status == OrderStatus.SHIPPED:
        background_tasks.add_task(
            email_service.send_order_shipped,
            user,
            updated_order
        )
    elif status_update.status == OrderStatus.DELIVERED:
        background_tasks.add_task(
            email_service.send_order_delivered,
            user,
            updated_order
        )
    
    return updated_order