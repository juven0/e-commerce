
"""
Repository pour Order
Gestion de l'accès aux données des commandes
"""

from typing import Optional, List
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.models.order import Order, OrderItem, OrderStatus
from app.repositories.base import BaseRepository


class OrderRepository(BaseRepository[Order]):
    """Repository pour gérer les commandes"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Order, db)
    
    async def get_by_id_with_details(self, order_id: int) -> Optional[Order]:
        """
        Récupère une commande avec tous ses détails
        
        Args:
            order_id: ID de la commande
        
        Returns:
            Commande avec relations
        """
        query = (
            select(Order)
            .where(Order.id == order_id)
            .options(
                selectinload(Order.items).selectinload(OrderItem.product),
                selectinload(Order.billing_address),
                selectinload(Order.shipping_address),
                selectinload(Order.payments),
                selectinload(Order.coupons)
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_user_id(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Order]:
        """
        Récupère les commandes d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            skip: Offset
            limit: Limite
        
        Returns:
            Liste de commandes
        """
        query = (
            select(Order)
            .where(Order.user_id == user_id)
            .options(selectinload(Order.items))
            .offset(skip)
            .limit(limit)
            .order_by(Order.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_status(
        self,
        status: OrderStatus,
        skip: int = 0,
        limit: int = 100
    ) -> List[Order]:
        """
        Récupère les commandes par statut
        
        Args:
            status: Statut recherché
            skip: Offset
            limit: Limite
        
        Returns:
            Liste de commandes
        """
        query = (
            select(Order)
            .where(Order.status == status)
            .options(selectinload(Order.items))
            .offset(skip)
            .limit(limit)
            .order_by(Order.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_user_and_status(
        self,
        user_id: int,
        status: OrderStatus,
        skip: int = 0,
        limit: int = 100
    ) -> List[Order]:
        """
        Récupère les commandes d'un utilisateur par statut
        
        Args:
            user_id: ID de l'utilisateur
            status: Statut recherché
            skip: Offset
            limit: Limite
        
        Returns:
            Liste de commandes
        """
        query = (
            select(Order)
            .where(
                and_(
                    Order.user_id == user_id,
                    Order.status == status
                )
            )
            .offset(skip)
            .limit(limit)
            .order_by(Order.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        skip: int = 0,
        limit: int = 100
    ) -> List[Order]:
        """
        Récupère les commandes dans une période
        
        Args:
            start_date: Date de début
            end_date: Date de fin
            skip: Offset
            limit: Limite
        
        Returns:
            Liste de commandes
        """
        query = (
            select(Order)
            .where(
                and_(
                    Order.created_at >= start_date,
                    Order.created_at <= end_date
                )
            )
            .offset(skip)
            .limit(limit)
            .order_by(Order.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def update_status(
        self,
        order_id: int,
        status: OrderStatus
    ) -> Optional[Order]:
        """
        Met à jour le statut d'une commande
        
        Args:
            order_id: ID de la commande
            status: Nouveau statut
        
        Returns:
            Commande mise à jour
        """
        return await self.update(order_id, {"status": status})
    
    async def count_by_status(self, status: OrderStatus) -> int:
        """
        Compte les commandes par statut
        
        Args:
            status: Statut à compter
        
        Returns:
            Nombre de commandes
        """
        return await self.count(status=status)
    
    async def count_by_user(self, user_id: int) -> int:
        """
        Compte les commandes d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
        
        Returns:
            Nombre de commandes
        """
        return await self.count(user_id=user_id)


class OrderItemRepository(BaseRepository[OrderItem]):
    """Repository pour gérer les articles de commande"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(OrderItem, db)
    
    async def get_by_order_id(self, order_id: int) -> List[OrderItem]:
        """
        Récupère les articles d'une commande
        
        Args:
            order_id: ID de la commande
        
        Returns:
            Liste des articles
        """
        query = (
            select(OrderItem)
            .where(OrderItem.order_id == order_id)
            .options(selectinload(OrderItem.product))
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def bulk_create_items(
        self,
        order_id: int,
        items: List[dict]
    ) -> List[OrderItem]:
        """
        Crée plusieurs articles de commande
        
        Args:
            order_id: ID de la commande
            items: Liste d'articles à créer
        
        Returns:
            Liste des articles créés
        """
        items_data = []
        for item in items:
            items_data.append({
                "order_id": order_id,
                "product_id": item["product_id"],
                "quantity": item["quantity"],
                "unit_price": item["unit_price"]
            })
        
        return await self.bulk_create(items_data)