
"""
Routes API - Produits
CRUD produits, recherche, filtres
"""

from typing import Optional
from decimal import Decimal
from fastapi import APIRouter, HTTPException, status, Query

from app.api.dependencies import (
    DatabaseDep,
    StaffUser,
    PaginationDep,
    create_paginated_response
)
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductDetailResponse,
    ProductUpdateStock,
    ProductFilterParams
)
from app.services.product import ProductService


router = APIRouter(prefix="/products", tags=["Products"])


# ===== Routes publiques =====

@router.get(
    "",
    response_model=dict,
    summary="Liste des produits"
)
async def get_products(
    pagination: PaginationDep,
    category_id: Optional[int] = Query(None, description="Filtrer par catégorie"),
    min_price: Optional[Decimal] = Query(None, ge=0, description="Prix minimum"),
    max_price: Optional[Decimal] = Query(None, ge=0, description="Prix maximum"),
    in_stock: Optional[bool] = Query(None, description="En stock uniquement"),
    on_sale: Optional[bool] = Query(None, description="En promotion uniquement"),
    search: Optional[str] = Query(None, min_length=2, description="Recherche"),
    db: DatabaseDep = None
):
    """
    Récupère la liste des produits avec filtres et pagination
    
    - Pagination
    - Recherche par nom/description/SKU
    - Filtrage par catégorie, prix, stock, promotion
    """
    product_service = ProductService(db)
    
    filters = ProductFilterParams(
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        in_stock=in_stock,
        on_sale=on_sale,
        search=search,
        is_active=True
    )
    
    products, total = await product_service.get_products(
        filters,
        pagination.skip,
        pagination.limit
    )
    
    return create_paginated_response(
        items=[ProductResponse.model_validate(p) for p in products],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size
    )


@router.get(
    "/{product_id}",
    response_model=ProductDetailResponse,
    summary="Détails d'un produit"
)
async def get_product(
    product_id: int,
    db: DatabaseDep
):
    """
    Récupère les détails complets d'un produit
    
    - Informations du produit
    - Images
    - Catégories
    - Note moyenne et avis
    """
    product_service = ProductService(db)
    
    product = await product_service.get_product_by_id(product_id)
    
    return product


@router.get(
    "/slug/{slug}",
    response_model=ProductDetailResponse,
    summary="Produit par slug"
)
async def get_product_by_slug(
    slug: str,
    db: DatabaseDep
):
    """
    Récupère un produit par son slug (URL-friendly)
    
    Utile pour les URLs SEO: /products/iphone-15-pro
    """
    product_service = ProductService(db)
    
    product = await product_service.get_product_by_slug(slug)
    
    return product


# ===== Routes admin/manager =====

@router.post(
    "",
    response_model=ProductDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un produit (Staff)"
)
async def create_product(
    product_data: ProductCreate,
    staff_user: StaffUser,
    db: DatabaseDep
):
    """
    Crée un nouveau produit
    
    **Réservé au staff (admin/manager)**
    
    - Génère automatiquement le slug si non fourni
    - Vérifie l'unicité du slug et SKU
    """
    product_service = ProductService(db)
    
    product = await product_service.create_product(product_data)
    
    return product


@router.put(
    "/{product_id}",
    response_model=ProductDetailResponse,
    summary="Mettre à jour un produit (Staff)"
)
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    staff_user: StaffUser,
    db: DatabaseDep
):
    """
    Met à jour un produit
    
    **Réservé au staff (admin/manager)**
    """
    product_service = ProductService(db)
    
    updated_product = await product_service.update_product(
        product_id,
        product_update
    )
    
    return updated_product


@router.patch(
    "/{product_id}/stock",
    response_model=ProductResponse,
    summary="Mettre à jour le stock (Staff)"
)
async def update_product_stock(
    product_id: int,
    stock_update: ProductUpdateStock,
    staff_user: StaffUser,
    db: DatabaseDep
):
    """
    Met à jour le stock d'un produit
    
    **Réservé au staff (admin/manager)**
    """
    product_service = ProductService(db)
    
    updated_product = await product_service.update_stock(
        product_id,
        stock_update.stock
    )
    
    return updated_product


@router.patch(
    "/{product_id}/stock/increase",
    response_model=ProductResponse,
    summary="Augmenter le stock (Staff)"
)
async def increase_stock(
    product_id: int,
    quantity: int = Query(..., gt=0, description="Quantité à ajouter"),
    staff_user: StaffUser = None,
    db: DatabaseDep = None
):
    """
    Augmente le stock d'un produit
    
    **Réservé au staff (admin/manager)**
    """
    product_service = ProductService(db)
    
    updated_product = await product_service.increase_stock(product_id, quantity)
    
    return updated_product


@router.patch(
    "/{product_id}/stock/decrease",
    response_model=ProductResponse,
    summary="Diminuer le stock (Staff)"
)
async def decrease_stock(
    product_id: int,
    quantity: int = Query(..., gt=0, description="Quantité à retirer"),
    staff_user: StaffUser = None,
    db: DatabaseDep = None
):
    """
    Diminue le stock d'un produit
    
    **Réservé au staff (admin/manager)**
    
    Vérifie que le stock ne devient pas négatif
    """
    product_service = ProductService(db)
    
    updated_product = await product_service.decrease_stock(product_id, quantity)
    
    return updated_product


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer un produit (Staff)"
)
async def delete_product(
    product_id: int,
    staff_user: StaffUser,
    db: DatabaseDep
):
    """
    Supprime un produit
    
    **Réservé au staff (admin/manager)**
    
    ⚠️ Action irréversible
    """
    product_service = ProductService(db)
    
    await product_service.delete_product(product_id)
    
    return None