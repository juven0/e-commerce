
"""
Repository pour Category
Gestion de l'accès aux données catégories
"""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.repositories.base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    """Repository pour gérer les catégories"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Category, db)
    
    async def get_by_slug(self, slug: str) -> Optional[Category]:
        """
        Récupère une catégorie par son slug
        
        Args:
            slug: Slug de la catégorie
        
        Returns:
            Catégorie ou None
        """
        query = (
            select(Category)
            .where(Category.slug == slug)
            .options(
                selectinload(Category.children),
                selectinload(Category.parent)
            )
        )
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
        query = select(Category.id).where(Category.slug == slug)
        
        if exclude_id:
            query = query.where(Category.id != exclude_id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def get_root_categories(self) -> List[Category]:
        """
        Récupère toutes les catégories racines (sans parent)
        
        Returns:
            Liste de catégories racines
        """
        query = (
            select(Category)
            .where(Category.parent_id.is_(None))
            .where(Category.is_active == True)
            .options(selectinload(Category.children))
            .order_by(Category.name)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_children(self, parent_id: int) -> List[Category]:
        """
        Récupère les sous-catégories d'une catégorie
        
        Args:
            parent_id: ID de la catégorie parente
        
        Returns:
            Liste de sous-catégories
        """
        query = (
            select(Category)
            .where(Category.parent_id == parent_id)
            .where(Category.is_active == True)
            .order_by(Category.name)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_tree(self) -> List[Category]:
        """
        Récupère l'arbre complet des catégories
        
        Returns:
            Liste hiérarchique de catégories
        """
        query = (
            select(Category)
            .where(Category.is_active == True)
            .options(
                selectinload(Category.children),
                selectinload(Category.parent)
            )
            .order_by(Category.parent_id.nullsfirst(), Category.name)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_active(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Category]:
        """
        Récupère les catégories actives
        
        Args:
            skip: Offset
            limit: Limite
        
        Returns:
            Liste de catégories actives
        """
        query = (
            select(Category)
            .where(Category.is_active == True)
            .offset(skip)
            .limit(limit)
            .order_by(Category.name)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def search(
        self,
        search_term: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Category]:
        """
        Recherche de catégories par nom ou description
        
        Args:
            search_term: Terme de recherche
            skip: Offset
            limit: Limite
        
        Returns:
            Liste de catégories correspondantes
        """
        search_pattern = f"%{search_term}%"
        query = (
            select(Category)
            .where(Category.name.ilike(search_pattern))
            .where(Category.is_active == True)
            .offset(skip)
            .limit(limit)
            .order_by(Category.name)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def has_products(self, category_id: int) -> bool:
        """
        Vérifie si une catégorie contient des produits
        
        Args:
            category_id: ID de la catégorie
        
        Returns:
            True si contient des produits
        """
        category = await self.get_by_id(category_id)
        if not category:
            return False
        
        return len(category.products) > 0 if category.products else False
    
    async def has_children(self, category_id: int) -> bool:
        """
        Vérifie si une catégorie a des sous-catégories
        
        Args:
            category_id: ID de la catégorie
        
        Returns:
            True si a des sous-catégories
        """
        children = await self.get_children(category_id)
        return len(children) > 0