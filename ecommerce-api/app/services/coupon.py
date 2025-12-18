
"""
Service de gestion des coupons
Validation et application des coupons de réduction
"""

from typing import Optional, List, Tuple
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from app.models.coupon import Coupon
from app.repositories.coupon import CouponRepository
from app.schemas.coupon import CouponCreate, CouponUpdate, CouponValidateRequest


class CouponService:
    """Service de gestion des coupons"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.coupon_repo = CouponRepository(db)
    
    async def create_coupon(self, coupon_data: CouponCreate) -> Coupon:
        """
        Crée un nouveau coupon
        
        Args:
            coupon_data: Données du coupon
        
        Returns:
            Coupon créé
        
        Raises:
            HTTPException: Si code existe déjà
        """
        # Vérifier que le code n'existe pas déjà
        if await self.coupon_repo.code_exists(coupon_data.code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ce code promo existe déjà"
            )
        
        # Créer le coupon
        coupon_dict = coupon_data.model_dump()
        coupon = await self.coupon_repo.create(coupon_dict)
        
        return coupon
    
    async def get_coupon_by_id(self, coupon_id: int) -> Coupon:
        """
        Récupère un coupon par son ID
        
        Args:
            coupon_id: ID du coupon
        
        Returns:
            Coupon
        
        Raises:
            HTTPException: Si coupon non trouvé
        """
        coupon = await self.coupon_repo.get_by_id(coupon_id)
        
        if not coupon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Coupon non trouvé"
            )
        
        return coupon
    
    async def get_coupon_by_code(self, code: str) -> Coupon:
        """
        Récupère un coupon par son code
        
        Args:
            code: Code promo
        
        Returns:
            Coupon
        
        Raises:
            HTTPException: Si coupon non trouvé
        """
        coupon = await self.coupon_repo.get_by_code(code)
        
        if not coupon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Code promo non trouvé"
            )
        
        return coupon
    
    async def update_coupon(
        self,
        coupon_id: int,
        coupon_update: CouponUpdate
    ) -> Coupon:
        """
        Met à jour un coupon
        
        Args:
            coupon_id: ID du coupon
            coupon_update: Données à mettre à jour
        
        Returns:
            Coupon mis à jour
        
        Raises:
            HTTPException: Si coupon non trouvé
        """
        # Vérifier que le coupon existe
        await self.get_coupon_by_id(coupon_id)
        
        # Mettre à jour
        update_data = coupon_update.model_dump(exclude_unset=True)
        updated_coupon = await self.coupon_repo.update(coupon_id, update_data)
        
        return updated_coupon
    
    async def delete_coupon(self, coupon_id: int) -> bool:
        """
        Supprime un coupon
        
        Args:
            coupon_id: ID du coupon
        
        Returns:
            True si supprimé
        
        Raises:
            HTTPException: Si coupon non trouvé
        """
        await self.get_coupon_by_id(coupon_id)
        
        deleted = await self.coupon_repo.delete(coupon_id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur lors de la suppression"
            )
        
        return True
    
    async def validate_coupon(
        self,
        code: str,
        order_amount: Decimal
    ) -> tuple[bool, Optional[Coupon], Optional[str], Decimal, Decimal]:
        """
        Valide un coupon pour un montant de commande
        
        Args:
            code: Code promo
            order_amount: Montant de la commande
        
        Returns:
            (is_valid, coupon, error_message, discount_amount, final_amount)
        """
        # Valider le code
        is_valid, coupon, error = await self.coupon_repo.validate_code(code)
        
        if not is_valid:
            return False, coupon, error, Decimal("0"), order_amount
        
        # Vérifier le montant minimum
        if coupon.min_order_amount and order_amount < coupon.min_order_amount:
            error_msg = (
                f"Montant minimum requis: {coupon.min_order_amount}€. "
                f"Votre panier: {order_amount}€"
            )
            return False, coupon, error_msg, Decimal("0"), order_amount
        
        # Calculer la réduction
        discount_amount = Decimal(str(coupon.calculate_discount(float(order_amount))))
        final_amount = order_amount - discount_amount
        
        return True, coupon, None, discount_amount, final_amount
    
    async def get_all_coupons(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False,
        valid_only: bool = False
    ) -> Tuple[List[Coupon], int]:
        """
        Récupère tous les coupons avec filtres
        
        Args:
            skip: Offset
            limit: Limite
            active_only: Coupons actifs uniquement
            valid_only: Coupons valides uniquement
        
        Returns:
            (Liste de coupons, Total)
        """
        if valid_only:
            coupons = await self.coupon_repo.get_valid_coupons(skip, limit)
            total = await self.coupon_repo.count_valid()
        elif active_only:
            coupons = await self.coupon_repo.get_active_coupons(skip, limit)
            total = await self.coupon_repo.count_active()
        else:
            coupons = await self.coupon_repo.get_all(skip, limit)
            total = await self.coupon_repo.count()
        
        return coupons, total
    
    async def activate_coupon(self, coupon_id: int) -> Coupon:
        """
        Active un coupon
        
        Args:
            coupon_id: ID du coupon
        
        Returns:
            Coupon activé
        
        Raises:
            HTTPException: Si coupon non trouvé
        """
        await self.get_coupon_by_id(coupon_id)
        
        activated_coupon = await self.coupon_repo.activate(coupon_id)
        
        return activated_coupon
    
    async def deactivate_coupon(self, coupon_id: int) -> Coupon:
        """
        Désactive un coupon
        
        Args:
            coupon_id: ID du coupon
        
        Returns:
            Coupon désactivé
        
        Raises:
            HTTPException: Si coupon non trouvé
        """
        await self.get_coupon_by_id(coupon_id)
        
        deactivated_coupon = await self.coupon_repo.deactivate(coupon_id)
        
        return deactivated_coupon
    
    async def get_coupon_usage(self, coupon_id: int) -> dict:
        """
        Récupère les statistiques d'utilisation d'un coupon
        
        Args:
            coupon_id: ID du coupon
        
        Returns:
            Dictionnaire de statistiques
        
        Raises:
            HTTPException: Si coupon non trouvé
        """
        coupon = await self.get_coupon_by_id(coupon_id)
        
        usage_count = await self.coupon_repo.get_usage_count(coupon_id)
        
        # Calculer le total des réductions données
        total_discount = Decimal("0")
        if coupon.orders:
            for order in coupon.orders:
                discount = Decimal(str(coupon.calculate_discount(float(order.total_amount))))
                total_discount += discount
        
        return {
            "coupon_code": coupon.code,
            "usage_count": usage_count,
            "total_discount_given": float(total_discount),
            "is_active": coupon.is_active,
            "is_valid": coupon.is_valid
        }
    
    async def get_coupon_statistics(self) -> dict:
        """
        Récupère les statistiques globales des coupons (admin)
        
        Returns:
            Dictionnaire de statistiques
        """
        total = await self.coupon_repo.count()
        active = await self.coupon_repo.count_active()
        valid = await self.coupon_repo.count_valid()
        
        return {
            "total_coupons": total,
            "active": active,
            "valid": valid,
            "inactive": total - active
        }