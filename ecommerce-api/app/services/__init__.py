
"""
Module services - Tous les services
Importations centralisées pour faciliter l'usage
"""

from app.services.auth import AuthService
from app.services.user import UserService
from app.services.product import ProductService
from app.services.cart import CartService
from app.services.order import OrderService
from app.services.payment import PaymentService
from app.services.coupon import CouponService
from app.services.email import EmailService


__all__ = [
    "AuthService",
    "UserService",
    "ProductService",
    "CartService",
    "OrderService",
    "PaymentService",
    "CouponService",
    "EmailService",
]