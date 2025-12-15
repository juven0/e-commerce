
"""
Module models - Tous les modèles SQLAlchemy
Importations centralisées pour faciliter l'usage
"""

from app.models.base import BaseModel, TimestampMixin
from app.models.user import User, UserRole
from app.models.address import Address, AddressType
from app.models.category import Category
from app.models.product import Product, ProductImage, product_categories
from app.models.cart import Cart, CartItem
from app.models.order import Order, OrderItem, OrderStatus, order_coupons
from app.models.payment import Payment, PaymentMethod, PaymentStatus
from app.models.review import Review
from app.models.coupon import Coupon, DiscountType
from app.models.activity_log import ActivityLog


__all__ = [
    # Base
    "BaseModel",
    "TimestampMixin",
    
    # User
    "User",
    "UserRole",
    
    # Address
    "Address",
    "AddressType",
    
    # Category
    "Category",
    
    # Product
    "Product",
    "ProductImage",
    "product_categories",
    
    # Cart
    "Cart",
    "CartItem",
    
    # Order
    "Order",
    "OrderItem",
    "OrderStatus",
    "order_coupons",
    
    # Payment
    "Payment",
    "PaymentMethod",
    "PaymentStatus",
    
    # Review
    "Review",
    
    # Coupon
    "Coupon",
    "DiscountType",
    
    # Activity Log
    "ActivityLog",
]