
"""
Service de gestion des commandes
Création et gestion des commandes
"""

from typing import Optional, List, Tuple
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from app.models.order import Order, OrderStatus
from app.repositories.order import OrderRepository, OrderItemRepository
from app.repositories.cart import CartRepository, CartItemRepository
from app.repositories.product import ProductRepository
from app.repositories.coupon import CouponRepository
from app.schemas.order import OrderCreate, OrderFromCart


class OrderService:
    """Service de gestion des commandes"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.order_repo = OrderRepository(db)
        self.order_item_repo = OrderItemRepository(db)
        self.cart_repo = CartRepository(db)
        self.cart_item_repo = CartItemRepository(db)
        self.product_repo = ProductRepository(db)
        self.coupon_repo = CouponRepository(db)
    
    async def create_order_from_cart(
        self,
        user_id: int,
        order_data: OrderFromCart
    ) -> Order:
        """
        Crée une commande depuis le panier
        
        Args:
            user_id: ID de l'utilisateur
            order_data: Données de la commande
        
        Returns:
            Commande créée
        
        Raises:
            HTTPException: Si panier vide ou stock insuffisant
        """
        # Récupérer le panier
        cart = await self.cart_repo.get_by_user_id(user_id)
        
        if not cart or cart.is_empty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le panier est vide"
            )
        
        # Valider la disponibilité des produits
        for cart_item in cart.items:
            product = await self.product_repo.get_by_id(cart_item.product_id)
            
            if not product or not product.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Le produit {cart_item.product_id} n'est plus disponible"
                )
            
            if product.stock < cart_item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Stock insuffisant pour {product.name}"
                )
        
        # Calculer le total
        total_amount = Decimal(str(cart.subtotal))
        
        # Appliquer le coupon si fourni
        discount_amount = Decimal("0")
        if order_data.coupon_code:
            is_valid, coupon, error = await self.coupon_repo.validate_code(
                order_data.coupon_code
            )
            
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error or "Code promo invalide"
                )
            
            discount_amount = Decimal(str(coupon.calculate_discount(float(total_amount))))
            total_amount -= discount_amount
        
        # Créer la commande
        order_dict = {
            "user_id": user_id,
            "status": OrderStatus.PENDING,
            "total_amount": total_amount,
            "billing_address_id": order_data.billing_address_id,
            "shipping_address_id": order_data.shipping_address_id
        }
        
        order = await self.order_repo.create(order_dict)
        
        # Créer les items de commande
        order_items_data = []
        for cart_item in cart.items:
            order_items_data.append({
                "product_id": cart_item.product_id,
                "quantity": cart_item.quantity,
                "unit_price": cart_item.price
            })
        
        await self.order_item_repo.bulk_create_items(order.id, order_items_data)
        
        # Diminuer le stock des produits
        for cart_item in cart.items:
            await self.product_repo.decrease_stock(
                cart_item.product_id,
                cart_item.quantity
            )
        
        # Vider le panier
        await self.cart_repo.clear(cart.id)
        
        # Recharger la commande avec les détails
        order_with_details = await self.order_repo.get_by_id_with_details(order.id)
        
        return order_with_details
    
    async def get_order_by_id(
        self,
        order_id: int,
        user_id: Optional[int] = None
    ) -> Order:
        """
        Récupère une commande par son ID
        
        Args:
            order_id: ID de la commande
            user_id: ID de l'utilisateur (pour vérifier l'appartenance)
        
        Returns:
            Commande avec détails
        
        Raises:
            HTTPException: Si commande non trouvée ou non autorisée
        """
        order = await self.order_repo.get_by_id_with_details(order_id)
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Commande non trouvée"
            )
        
        # Vérifier l'appartenance si user_id fourni
        if user_id and order.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vous n'avez pas accès à cette commande"
            )
        
        return order
    
    async def get_user_orders(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Order], int]:
        """
        Récupère les commandes d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            skip: Offset
            limit: Limite
        
        Returns:
            (Liste de commandes, Total)
        """
        orders = await self.order_repo.get_by_user_id(user_id, skip, limit)
        total = await self.order_repo.count_by_user(user_id)
        
        return orders, total
    
    async def get_all_orders(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[OrderStatus] = None
    ) -> Tuple[List[Order], int]:
        """
        Récupère toutes les commandes (admin)
        
        Args:
            skip: Offset
            limit: Limite
            status: Filtrer par statut
        
        Returns:
            (Liste de commandes, Total)
        """
        if status:
            orders = await self.order_repo.get_by_status(status, skip, limit)
            total = await self.order_repo.count_by_status(status)
        else:
            orders = await self.order_repo.get_all(skip, limit)
            total = await self.order_repo.count()
        
        return orders, total
    
    async def update_order_status(
        self,
        order_id: int,
        new_status: OrderStatus
    ) -> Order:
        """
        Met à jour le statut d'une commande (admin)
        
        Args:
            order_id: ID de la commande
            new_status: Nouveau statut
        
        Returns:
            Commande mise à jour
        
        Raises:
            HTTPException: Si commande non trouvée
        """
        order = await self.get_order_by_id(order_id)
        
        updated_order = await self.order_repo.update_status(order_id, new_status)
        
        return updated_order
    
    async def cancel_order(
        self,
        order_id: int,
        user_id: Optional[int] = None
    ) -> Order:
        """
        Annule une commande
        
        Args:
            order_id: ID de la commande
            user_id: ID de l'utilisateur (pour vérifier l'appartenance)
        
        Returns:
            Commande annulée
        
        Raises:
            HTTPException: Si commande ne peut pas être annulée
        """
        order = await self.get_order_by_id(order_id, user_id)
        
        if not order.can_be_cancelled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cette commande ne peut plus être annulée"
            )
        
        # Restaurer le stock
        for item in order.items:
            await self.product_repo.increase_stock(
                item.product_id,
                item.quantity
            )
        
        # Mettre à jour le statut
        cancelled_order = await self.order_repo.update_status(
            order_id,
            OrderStatus.CANCELLED
        )
        
        return cancelled_order
    
    async def get_order_statistics(self) -> dict:
        """
        Récupère les statistiques des commandes (admin)
        
        Returns:
            Dictionnaire de statistiques
        """
        total = await self.order_repo.count()
        pending = await self.order_repo.count_by_status(OrderStatus.PENDING)
        paid = await self.order_repo.count_by_status(OrderStatus.PAID)
        shipped = await self.order_repo.count_by_status(OrderStatus.SHIPPED)
        delivered = await self.order_repo.count_by_status(OrderStatus.DELIVERED)
        cancelled = await self.order_repo.count_by_status(OrderStatus.CANCELLED)
        
        return {
            "total": total,
            "pending": pending,
            "paid": paid,
            "shipped": shipped,
            "delivered": delivered,
            "cancelled": cancelled
        }   