
"""
Repository pour Product
Gestion de l'accès aux données produits
"""

from typing import Optional, List
from sqlalchemy import select, or_, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from app.models.product import Product, ProductImage
from app.models.category import Category
from app.repositories.base import BaseRepository


class ProductRepository(BaseRepository[Product]):
    """Repository pour gérer les produits"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Product, db)
    
    async def get_by_slug(self, slug: str) -> Optional[Product]:
        """
        Récupère un produit par son slug
        
        Args:
            slug: Slug du produit
        
        Returns:
            Produit ou None
        """
        query = (
            select(Product)
            .where(Product.slug == slug)
            .options(
                selectinload(Product.images),
                selectinload(Product.categories),
                selectinload(Product.reviews)
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_sku(self, sku: str) -> Optional[Product]:
        """
        Récupère un produit par son SKU
        
        Args:
            sku: SKU du produit
        
        Returns:
            Produit ou None
        """
        query = select(Product).where(Product.sku == sku)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def slug_exists(self, slug: str, exclude_id: Optional[int] = None) -> bool:
        """
        Vérifie si un slug existe déjà
        
        Args:
            slug: Slug à vérifier
            exclude_id: ID à exclure
        
        Returns:
            True si existe, False sinon
        """
        query = select(Product.id).where(Product.slug == slug)
        
        if exclude_id:
            query = query.where(Product.id != exclude_id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def sku_exists(self, sku: str, exclude_id: Optional[int] = None) -> bool:
        """
        Vérifie si un SKU existe déjà
        
        Args:
            sku: SKU à vérifier
            exclude_id: ID à exclure
        
        Returns:
            True si existe, False sinon
        """
        query = select(Product.id).where(Product.sku == sku)
        
        if exclude_id:
            query = query.where(Product.id != exclude_id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def get_active(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:
        """
        Récupère les produits actifs
        
        Args:
            skip: Offset
            limit: Limite
        
        Returns:
            Liste de produits actifs
        """
        query = (
            select(Product)
            .where(Product.is_active == True)
            .options(selectinload(Product.images))
            .offset(skip)
            .limit(limit)
            .order_by(Product.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_category(
        self,
        category_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:
        """
        Récupère les produits d'une catégorie
        
        Args:
            category_id: ID de la catégorie
            skip: Offset
            limit: Limite
        
        Returns:
            Liste de produits
        """
        query = (
            select(Product)
            .join(Product.categories)
            .where(Category.id == category_id)
            .where(Product.is_active == True)
            .options(selectinload(Product.images))
            .offset(skip)
            .limit(limit)
            .order_by(Product.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_in_stock(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:
        """
        Récupère les produits en stock
        
        Args:
            skip: Offset
            limit: Limite
        
        Returns:
            Liste de produits en stock
        """
        query = (
            select(Product)
            .where(
                and_(
                    Product.is_active == True,
                    Product.stock > 0
                )
            )
            .options(selectinload(Product.images))
            .offset(skip)
            .limit(limit)
            .order_by(Product.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_on_sale(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:
        """
        Récupère les produits en promotion
        
        Args:
            skip: Offset
            limit: Limite
        
        Returns:
            Liste de produits en promo
        """
        query = (
            select(Product)
            .where(
                and_(
                    Product.is_active == True,
                    Product.sale_price.is_not(None),
                    Product.sale_price > 0
                )
            )
            .options(selectinload(Product.images))
            .offset(skip)
            .limit(limit)
            .order_by(Product.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_price_range(
        self,
        min_price: Decimal,
        max_price: Decimal,
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:
        """
        Récupère les produits dans une fourchette de prix
        
        Args:
            min_price: Prix minimum
            max_price: Prix maximum
            skip: Offset
            limit: Limite
        
        Returns:
            Liste de produits
        """
        query = (
            select(Product)
            .where(
                and_(
                    Product.is_active == True,
                    Product.price >= min_price,
                    Product.price <= max_price
                )
            )
            .options(selectinload(Product.images))
            .offset(skip)
            .limit(limit)
            .order_by(Product.price.asc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def search(
        self,
        search_term: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:
        """
        Recherche de produits par nom ou description
        
        Args:
            search_term: Terme de recherche
            skip: Offset
            limit: Limite
        
        Returns:
            Liste de produits correspondants
        """
        search_pattern = f"%{search_term}%"
        query = (
            select(Product)
            .where(
                and_(
                    Product.is_active == True,
                    or_(
                        Product.name.ilike(search_pattern),
                        Product.description.ilike(search_pattern),
                        Product.sku.ilike(search_pattern)
                    )
                )
            )
            .options(selectinload(Product.images))
            .offset(skip)
            .limit(limit)
            .order_by(Product.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def update_stock(self, product_id: int, quantity: int) -> Optional[Product]:
        """
        Met à jour le stock d'un produit
        
        Args:
            product_id: ID du produit
            quantity: Nouvelle quantité
        
        Returns:
            Produit mis à jour
        """
        return await self.update(product_id, {"stock": quantity})
    
    async def decrease_stock(self, product_id: int, quantity: int) -> Optional[Product]:
        """
        Diminue le stock d'un produit
        
        Args:
            product_id: ID du produit
            quantity: Quantité à retirer
        
        Returns:
            Produit mis à jour
        """
        product = await self.get_by_id(product_id)
        if not product:
            return None
        
        new_stock = max(0, product.stock - quantity)
        return await self.update_stock(product_id, new_stock)
    
    async def increase_stock(self, product_id: int, quantity: int) -> Optional[Product]:
        """
        Augmente le stock d'un produit
        
        Args:
            product_id: ID du produit
            quantity: Quantité à ajouter
        
        Returns:
            Produit mis à jour
        """
        product = await self.get_by_id(product_id)
        if not product:
            return None
        
        new_stock = product.stock + quantity
        return await self.update_stock(product_id, new_stock)
    
    async def add_to_category(self, product_id: int, category_id: int) -> bool:
        """
        Ajoute un produit à une catégorie
        
        Args:
            product_id: ID du produit
            category_id: ID de la catégorie
        
        Returns:
            True si succès
        """
        product = await self.get_by_id(product_id)
        if not product:
            return False
        
        category = await self.db.get(Category, category_id)
        if not category:
            return False
        
        if category not in product.categories:
            product.categories.append(category)
            await self.db.flush()
        
        return True
    
    async def remove_from_category(self, product_id: int, category_id: int) -> bool:
        """
        Retire un produit d'une catégorie
        
        Args:
            product_id: ID du produit
            category_id: ID de la catégorie
        
        Returns:
            True si succès
        """
        product = await self.get_by_id(product_id)
        if not product:
            return False
        
        category = await self.db.get(Category, category_id)
        if not category:
            return False
        
        if category in product.categories:
            product.categories.remove(category)
            await self.db.flush()
        
        return True