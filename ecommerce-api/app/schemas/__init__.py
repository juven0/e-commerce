
"""
Module schemas - Tous les schemas Pydantic
Importations centralisées pour faciliter l'usage
"""

# User schemas
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserRegister,
    UserUpdate,
    UserUpdatePassword,
    UserUpdateRole,
    UserUpdateStatus,
    UserResponse,
    UserPublicResponse,
    UserProfileResponse,
    UserListResponse,
    EmailVerificationRequest,
    EmailVerificationConfirm,
    PasswordResetRequest,
    PasswordResetConfirm,
)

# Auth schemas
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    UserInfo,
    RefreshTokenRequest,
    RefreshTokenResponse,
    LogoutResponse,
    TokenPayload,
    TokenVerifyRequest,
    TokenVerifyResponse,
    AuthErrorResponse,
    AuthSuccessResponse,
)

# Address schemas
from app.schemas.address import (
    AddressBase,
    AddressCreate,
    AddressUpdate,
    AddressResponse,
    AddressListResponse,
)

# Category schemas
from app.schemas.category import (
    CategoryBase,
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryWithChildrenResponse,
    CategoryWithParentResponse,
    CategoryTreeResponse,
    CategoryListResponse,
    CategoryFilterParams,
)

# Product schemas
from app.schemas.product import (
    ProductImageBase,
    ProductImageCreate,
    ProductImageResponse,
    ProductBase,
    ProductCreate,
    ProductUpdate,
    ProductUpdateStock,
    ProductResponse,
    ProductDetailResponse,
    ProductListResponse,
    ProductFilterParams,
)

# Cart schemas
from app.schemas.cart import (
    CartItemBase,
    CartItemCreate,
    CartItemUpdate,
    CartItemResponse,
    ProductCartResponse,
    CartResponse,
    CartSummaryResponse,
    AddToCartRequest,
    UpdateCartItemRequest,
    RemoveFromCartResponse,
    ClearCartResponse,
)

# Order schemas
from app.schemas.order import (
    OrderItemBase,
    OrderItemResponse,
    ProductOrderResponse,
    OrderCreate,
    OrderFromCart,
    OrderUpdateStatus,
    OrderCancel,
    OrderResponse,
    OrderDetailResponse,
    OrderListResponse,
    OrderFilterParams,
    OrderCreatedResponse,
    OrderCancelledResponse,
)

# Payment schemas
from app.schemas.payment import (
    PaymentBase,
    PaymentCreate,
    PaymentInitiate,
    PaymentResponse,
    PaymentDetailResponse,
    StripeWebhookEvent,
    PaypalWebhookEvent,
    PaymentConfirmation,
    PaymentSuccessResponse,
    PaymentFailedResponse,
    StripePaymentIntent,
    StripeCheckoutSession,
    PayPalOrderCreate,
    PayPalOrderCapture,
    RefundRequest,
    RefundResponse,
    PaymentListResponse,
)

# Review schemas
from app.schemas.review import (
    ReviewBase,
    ReviewCreate,
    ReviewUpdate,
    ReviewApprove,
    ReviewResponse,
    ReviewDetailResponse,
    ProductBasicResponse,
    ReviewListResponse,
    ReviewFilterParams,
    ReviewStats,
)

# Coupon schemas
from app.schemas.coupon import (
    CouponBase,
    CouponCreate,
    CouponUpdate,
    CouponResponse,
    CouponDetailResponse,
    CouponValidateRequest,
    CouponValidateResponse,
    CouponApplyRequest,
    CouponApplyResponse,
    CouponListResponse,
    CouponFilterParams,
    CouponStats,
)


__all__ = [
    # User
    "UserBase",
    "UserCreate",
    "UserRegister",
    "UserUpdate",
    "UserUpdatePassword",
    "UserUpdateRole",
    "UserUpdateStatus",
    "UserResponse",
    "UserPublicResponse",
    "UserProfileResponse",
    "UserListResponse",
    "EmailVerificationRequest",
    "EmailVerificationConfirm",
    "PasswordResetRequest",
    "PasswordResetConfirm",
    
    # Auth
    "LoginRequest",
    "LoginResponse",
    "UserInfo",
    "RefreshTokenRequest",
    "RefreshTokenResponse",
    "LogoutResponse",
    "TokenPayload",
    "TokenVerifyRequest",
    "TokenVerifyResponse",
    "AuthErrorResponse",
    "AuthSuccessResponse",
    
    # Address
    "AddressBase",
    "AddressCreate",
    "AddressUpdate",
    "AddressResponse",
    "AddressListResponse",
    
    # Category
    "CategoryBase",
    "CategoryCreate",
    "CategoryUpdate",
    "CategoryResponse",
    "CategoryWithChildrenResponse",
    "CategoryWithParentResponse",
    "CategoryTreeResponse",
    "CategoryListResponse",
    "CategoryFilterParams",
    
    # Product
    "ProductImageBase",
    "ProductImageCreate",
    "ProductImageResponse",
    "ProductBase",
    "ProductCreate",
    "ProductUpdate",
    "ProductUpdateStock",
    "ProductResponse",
    "ProductDetailResponse",
    "ProductListResponse",
    "ProductFilterParams",
    
    # Cart
    "CartItemBase",
    "CartItemCreate",
    "CartItemUpdate",
    "CartItemResponse",
    "ProductCartResponse",
    "CartResponse",
    "CartSummaryResponse",
    "AddToCartRequest",
    "UpdateCartItemRequest",
    "RemoveFromCartResponse",
    "ClearCartResponse",
    
    # Order
    "OrderItemBase",
    "OrderItemResponse",
    "ProductOrderResponse",
    "OrderCreate",
    "OrderFromCart",
    "OrderUpdateStatus",
    "OrderCancel",
    "OrderResponse",
    "OrderDetailResponse",
    "OrderListResponse",
    "OrderFilterParams",
    "OrderCreatedResponse",
    "OrderCancelledResponse",
    
    # Payment
    "PaymentBase",
    "PaymentCreate",
    "PaymentInitiate",
    "PaymentResponse",
    "PaymentDetailResponse",
    "StripeWebhookEvent",
    "PaypalWebhookEvent",
    "PaymentConfirmation",
    "PaymentSuccessResponse",
    "PaymentFailedResponse",
    "StripePaymentIntent",
    "StripeCheckoutSession",
    "PayPalOrderCreate",
    "PayPalOrderCapture",
    "RefundRequest",
    "RefundResponse",
    "PaymentListResponse",
    
    # Review
    "ReviewBase",
    "ReviewCreate",
    "ReviewUpdate",
    "ReviewApprove",
    "ReviewResponse",
    "ReviewDetailResponse",
    "ProductBasicResponse",
    "ReviewListResponse",
    "ReviewFilterParams",
    "ReviewStats",
    
    # Coupon
    "CouponBase",
    "CouponCreate",
    "CouponUpdate",
    "CouponResponse",
    "CouponDetailResponse",
    "CouponValidateRequest",
    "CouponValidateResponse",
    "CouponApplyRequest",
    "CouponApplyResponse",
    "CouponListResponse",
    "CouponFilterParams",
    "CouponStats",
]