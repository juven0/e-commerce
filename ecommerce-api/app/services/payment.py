
"""
Service de gestion des paiements
Intégration avec Stripe, PayPal, etc.
"""

from typing import Optional, List, Tuple
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.core.config import settings
from app.models.payment import Payment, PaymentStatus, PaymentMethod
from app.models.order import OrderStatus
from app.repositories.payment import PaymentRepository
from app.repositories.order import OrderRepository
from app.schemas.payment import PaymentCreate, PaymentInitiate


class PaymentService:
    """Service de gestion des paiements"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.payment_repo = PaymentRepository(db)
        self.order_repo = OrderRepository(db)
    
    async def initiate_payment(
        self,
        payment_data: PaymentInitiate,
        user_id: int
    ) -> Payment:
        """
        Initie un paiement pour une commande
        
        Args:
            payment_data: Données du paiement
            user_id: ID de l'utilisateur
        
        Returns:
            Paiement créé
        
        Raises:
            HTTPException: Si commande invalide
        """
        # Vérifier que la commande existe et appartient à l'utilisateur
        order = await self.order_repo.get_by_id_with_details(payment_data.order_id)
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Commande non trouvée"
            )
        
        if order.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cette commande ne vous appartient pas"
            )
        
        # Vérifier que la commande n'est pas déjà payée
        if order.is_paid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cette commande est déjà payée"
            )
        
        # Créer le paiement
        payment_dict = {
            "order_id": payment_data.order_id,
            "method": payment_data.method,
            "status": PaymentStatus.PENDING,
            "amount": order.total_amount
        }
        
        payment = await self.payment_repo.create(payment_dict)
        
        return payment
    
    async def process_payment(
        self,
        payment_id: int,
        transaction_reference: str
    ) -> Payment:
        """
        Traite un paiement (appelé par webhook ou callback)
        
        Args:
            payment_id: ID du paiement
            transaction_reference: Référence de transaction externe
        
        Returns:
            Paiement mis à jour
        
        Raises:
            HTTPException: Si paiement non trouvé
        """
        payment = await self.payment_repo.get_by_id(payment_id)
        
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paiement non trouvé"
            )
        
        # Marquer comme réussi
        updated_payment = await self.payment_repo.mark_as_success(
            payment_id,
            transaction_reference
        )
        
        # Mettre à jour le statut de la commande
        await self.order_repo.update_status(
            payment.order_id,
            OrderStatus.PAID
        )
        
        return updated_payment
    
    async def fail_payment(self, payment_id: int) -> Payment:
        """
        Marque un paiement comme échoué
        
        Args:
            payment_id: ID du paiement
        
        Returns:
            Paiement mis à jour
        """
        payment = await self.payment_repo.get_by_id(payment_id)
        
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paiement non trouvé"
            )
        
        updated_payment = await self.payment_repo.mark_as_failed(payment_id)
        
        return updated_payment
    
    async def refund_payment(
        self,
        payment_id: int,
        reason: Optional[str] = None
    ) -> Payment:
        """
        Rembourse un paiement
        
        Args:
            payment_id: ID du paiement
            reason: Raison du remboursement
        
        Returns:
            Paiement remboursé
        
        Raises:
            HTTPException: Si paiement ne peut pas être remboursé
        """
        payment = await self.payment_repo.get_by_id(payment_id)
        
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paiement non trouvé"
            )
        
        if not payment.can_be_refunded:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ce paiement ne peut pas être remboursé"
            )
        
        # Marquer comme remboursé
        refunded_payment = await self.payment_repo.mark_as_refunded(payment_id)
        
        # Mettre à jour le statut de la commande
        await self.order_repo.update_status(
            payment.order_id,
            OrderStatus.REFUNDED
        )
        
        return refunded_payment
    
    async def get_payment_by_id(self, payment_id: int) -> Payment:
        """
        Récupère un paiement par son ID
        
        Args:
            payment_id: ID du paiement
        
        Returns:
            Paiement
        
        Raises:
            HTTPException: Si paiement non trouvé
        """
        payment = await self.payment_repo.get_by_id(payment_id)
        
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paiement non trouvé"
            )
        
        return payment
    
    async def get_payments_by_order(self, order_id: int) -> List[Payment]:
        """
        Récupère tous les paiements d'une commande
        
        Args:
            order_id: ID de la commande
        
        Returns:
            Liste de paiements
        """
        payments = await self.payment_repo.get_by_order_id(order_id)
        return payments
    
    async def get_all_payments(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[PaymentStatus] = None,
        method: Optional[PaymentMethod] = None
    ) -> Tuple[List[Payment], int]:
        """
        Récupère tous les paiements avec filtres (admin)
        
        Args:
            skip: Offset
            limit: Limite
            status: Filtrer par statut
            method: Filtrer par méthode
        
        Returns:
            (Liste de paiements, Total)
        """
        if status:
            payments = await self.payment_repo.get_by_status(status, skip, limit)
            total = await self.payment_repo.count_by_status(status)
        elif method:
            payments = await self.payment_repo.get_by_method(method, skip, limit)
            total = await self.payment_repo.count_by_method(method)
        else:
            payments = await self.payment_repo.get_all(skip, limit)
            total = await self.payment_repo.count()
        
        return payments, total
    
    async def process_stripe_webhook(self, event_data: dict) -> Optional[Payment]:
        """
        Traite un webhook Stripe
        
        Args:
            event_data: Données de l'événement Stripe
        
        Returns:
            Paiement mis à jour ou None
        """
        event_type = event_data.get("type")
        
        if event_type == "payment_intent.succeeded":
            payment_intent = event_data.get("data", {}).get("object", {})
            payment_intent_id = payment_intent.get("id")
            
            # Récupérer le paiement par référence de transaction
            payment = await self.payment_repo.get_by_transaction_reference(
                payment_intent_id
            )
            
            if payment:
                return await self.process_payment(payment.id, payment_intent_id)
        
        elif event_type == "payment_intent.payment_failed":
            payment_intent = event_data.get("data", {}).get("object", {})
            payment_intent_id = payment_intent.get("id")
            
            payment = await self.payment_repo.get_by_transaction_reference(
                payment_intent_id
            )
            
            if payment:
                return await self.fail_payment(payment.id)
        
        return None
    
    async def process_paypal_webhook(self, event_data: dict) -> Optional[Payment]:
        """
        Traite un webhook PayPal
        
        Args:
            event_data: Données de l'événement PayPal
        
        Returns:
            Paiement mis à jour ou None
        """
        event_type = event_data.get("event_type")
        
        if event_type == "PAYMENT.CAPTURE.COMPLETED":
            resource = event_data.get("resource", {})
            capture_id = resource.get("id")
            
            payment = await self.payment_repo.get_by_transaction_reference(capture_id)
            
            if payment:
                return await self.process_payment(payment.id, capture_id)
        
        elif event_type == "PAYMENT.CAPTURE.DENIED":
            resource = event_data.get("resource", {})
            capture_id = resource.get("id")
            
            payment = await self.payment_repo.get_by_transaction_reference(capture_id)
            
            if payment:
                return await self.fail_payment(payment.id)
        
        return None
    
    async def get_payment_statistics(self) -> dict:
        """
        Récupère les statistiques des paiements (admin)
        
        Returns:
            Dictionnaire de statistiques
        """
        total = await self.payment_repo.count()
        successful = await self.payment_repo.count_by_status(PaymentStatus.SUCCESS)
        pending = await self.payment_repo.count_by_status(PaymentStatus.PENDING)
        failed = await self.payment_repo.count_by_status(PaymentStatus.FAILED)
        refunded = await self.payment_repo.count_by_status(PaymentStatus.REFUNDED)
        
        total_amount = await self.payment_repo.get_total_amount_by_status(
            PaymentStatus.SUCCESS
        )
        
        return {
            "total_payments": total,
            "successful": successful,
            "pending": pending,
            "failed": failed,
            "refunded": refunded,
            "total_revenue": total_amount
        }