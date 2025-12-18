
"""
Routes API - Panier
Gestion du panier d'achat
"""

from fastapi import APIRouter, HTTPException, status

from app.api.dependencies import DatabaseDep, CurrentUser
from app.schemas.cart import (
    CartResponse,
    CartItemResponse,
    AddToCartRequest,
    UpdateCartItemRequest,
    RemoveFromCartResponse,
    ClearCartResponse,
    CartSummaryResponse
)
from app.services.cart import CartService


router = APIRouter(prefix="/cart", tags=["Cart"])


@router.get(
    "",
    response_model=CartResponse,
    summary="Mon panier"
)
async def get_cart(
    current_user: CurrentUser,
    db: DatabaseDep
):
    """
    Récupère le panier de l'utilisateur connecté
    
    - Articles du panier avec détails des produits
    - Total et nombre d'articles
    """
    cart_service = CartService(db)
    
    cart = await cart_service.get_or_create_cart(current_user.id)
    
    return cart


@router.get(
    "/summary",
    response_model=CartSummaryResponse,
    summary="Résumé du panier"
)
async def get_cart_summary(
    current_user: CurrentUser,
    db: DatabaseDep
):
    """
    Récupère un résumé rapide du panier
    
    - Nombre total d'articles
    - Sous-total
    - Nombre de lignes
    """
    cart_service = CartService(db)
    
    summary = await cart_service.get_cart_total(current_user.id)
    
    return CartSummaryResponse(**summary)


@router.post(
    "/items",
    response_model=CartItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ajouter au panier"
)
async def add_to_cart(
    item_data: AddToCartRequest,
    current_user: CurrentUser,
    db: DatabaseDep
):
    """
    Ajoute un produit au panier
    
    - Si le produit existe déjà, augmente la quantité
    - Vérifie la disponibilité du stock
    - Utilise le prix actuel du produit
    """
    cart_service = CartService(db)
    
    cart_item = await cart_service.add_to_cart(current_user.id, item_data)
    
    return cart_item


@router.put(
    "/items/{item_id}",
    response_model=CartItemResponse,
    summary="Mettre à jour la quantité"
)
async def update_cart_item(
    item_id: int,
    item_update: UpdateCartItemRequest,
    current_user: CurrentUser,
    db: DatabaseDep
):
    """
    Met à jour la quantité d'un article du panier
    
    - Vérifie que l'article appartient à l'utilisateur
    - Vérifie le stock disponible
    """
    cart_service = CartService(db)
    
    updated_item = await cart_service.update_cart_item(
        current_user.id,
        item_id,
        item_update
    )
    
    return updated_item


@router.delete(
    "/items/{item_id}",
    response_model=RemoveFromCartResponse,
    summary="Retirer du panier"
)
async def remove_from_cart(
    item_id: int,
    current_user: CurrentUser,
    db: DatabaseDep
):
    """
    Retire un article du panier
    
    - Vérifie que l'article appartient à l'utilisateur
    """
    cart_service = CartService(db)
    
    await cart_service.remove_from_cart(current_user.id, item_id)
    
    return RemoveFromCartResponse()


@router.delete(
    "",
    response_model=ClearCartResponse,
    summary="Vider le panier"
)
async def clear_cart(
    current_user: CurrentUser,
    db: DatabaseDep
):
    """
    Vide complètement le panier
    
    ⚠️ Supprime tous les articles
    """
    cart_service = CartService(db)
    
    await cart_service.clear_cart(current_user.id)
    
    return ClearCartResponse()


@router.post(
    "/validate",
    response_model=dict,
    summary="Valider le panier"
)
async def validate_cart(
    current_user: CurrentUser,
    db: DatabaseDep
):
    """
    Valide le panier avant passage de commande
    
    - Vérifie que le panier n'est pas vide
    - Vérifie la disponibilité de tous les produits
    - Vérifie le stock pour chaque article
    
    Retourne les erreurs éventuelles
    """
    cart_service = CartService(db)
    
    is_valid, errors = await cart_service.validate_cart(current_user.id)
    
    return {
        "is_valid": is_valid,
        "errors": errors
    }