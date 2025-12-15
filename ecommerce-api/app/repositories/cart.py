
"""
Repository pour Cart
Gestion de l'accès aux données du panier
"""

from typing import Optional
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cart import Cart, CartItem
from app.repositories.base import BaseRepository


class CartRepository(BaseRepository[Cart]):
    """Repository pour gérer les paniers"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Cart, db)
    
    async def get_by_user_id(self, user_id: int) -> Optional[Cart]:
        """
        Récupère le panier d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
        
        Returns:
            Panier ou None
        """
        query = (
            select(Cart)
            .where(Cart.user_id == user_id)
            .options(
                selectinload(Cart.items).selectinload(CartItem.product)
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_or_create(self, user_id: int) -> Cart:
        """
        Récupère ou crée le panier d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
        
        Returns:
            Panier
        """
        cart = await self.get_by_user_id(user_id)
        
        if not cart:
            cart = await self.create({"user_id": user_id})
        
        return cart
    
    async def clear(self, cart_id: int) -> bool:
        """
        Vide un panier (supprime tous les articles)
        
        Args:
            cart_id: ID du panier
        
        Returns:
            True si succès
        """
        query = delete(CartItem).where(CartItem.cart_id == cart_id)
        await self.db.execute(query)
        await self.db.flush()
        return True
    
    async def get_items_count(self, cart_id: int) -> int:
        """
        Compte le nombre d'articles dans un panier
        
        Args:
            cart_id: ID du panier
        
        Returns:
            Nombre d'articles
        """
        cart = await self.get_by_id(cart_id)
        if not cart or not cart.items:
            return 0
        
        return sum(item.quantity for item in cart.items)


class CartItemRepository(BaseRepository[CartItem]):
    """Repository pour gérer les articles du panier"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(CartItem, db)
    
    async def get_by_cart_and_product(
        self,
        cart_id: int,
        product_id: int
    ) -> Optional[CartItem]:
        """
        Récupère un article spécifique du panier
        
        Args:
            cart_id: ID du panier
            product_id: ID du produit
        
        Returns:
            Article du panier ou None
        """
        query = (
            select(CartItem)
            .where(
                CartItem.cart_id == cart_id,
                CartItem.product_id == product_id
            )
            .options(selectinload(CartItem.product))
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def add_item(
        self,
        cart_id: int,
        product_id: int,
        quantity: int,
        price: float
    ) -> CartItem:
        """
        Ajoute un article au panier ou met à jour la quantité
        
        Args:
            cart_id: ID du panier
            product_id: ID du produit
            quantity: Quantité
            price: Prix unitaire
        
        Returns:
            Article du panier
        """
        # Vérifier si l'article existe déjà
        existing_item = await self.get_by_cart_and_product(cart_id, product_id)
        
        if existing_item:
            # Mettre à jour la quantité
            new_quantity = existing_item.quantity + quantity
            return await self.update(existing_item.id, {"quantity": new_quantity})
        else:
            # Créer un nouvel article
            return await self.create({
                "cart_id": cart_id,
                "product_id": product_id,
                "quantity": quantity,
                "price": price
            })
    
    async def update_quantity(
        self,
        item_id: int,
        quantity: int
    ) -> Optional[CartItem]:
        """
        Met à jour la quantité d'un article
        
        Args:
            item_id: ID de l'article
            quantity: Nouvelle quantité
        
        Returns:
            Article mis à jour
        """
        return await self.update(item_id, {"quantity": quantity})
    
    async def remove_item(self, item_id: int) -> bool:
        """
        Supprime un article du panier
        
        Args:
            item_id: ID de l'article
        
        Returns:
            True si supprimé
        """
        return await self.delete(item_id)
    
    async def get_cart_items(self, cart_id: int) -> list[CartItem]:
        """
        Récupère tous les articles d'un panier
        
        Args:
            cart_id: ID du panier
        
        Returns:
            Liste des articles
        """
        query = (
            select(CartItem)
            .where(CartItem.cart_id == cart_id)
            .options(selectinload(CartItem.product))
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())