
"""
Routes API - Authentification
Inscription, connexion, tokens, vérification email
"""

from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import DatabaseDep, CurrentUser
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    LogoutResponse,
    AuthSuccessResponse
)
from app.schemas.user import (
    UserRegister,
    UserResponse,
    EmailVerificationRequest,
    EmailVerificationConfirm,
    PasswordResetRequest,
    PasswordResetConfirm,
    UserUpdatePassword
)
from app.services.auth import AuthService
from app.services.email import EmailService
from app.core.security import create_email_verification_token, create_password_reset_token


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Inscription utilisateur"
)
async def register(
    user_data: UserRegister,
    background_tasks: BackgroundTasks,
    db: DatabaseDep
):
    """
    Inscription d'un nouvel utilisateur
    
    - Crée un nouveau compte utilisateur
    - Envoie un email de bienvenue
    - Envoie un email de vérification
    """
    auth_service = AuthService(db)
    email_service = EmailService()
    
    # Créer l'utilisateur
    user = await auth_service.register(user_data)
    
    # Envoyer les emails en arrière-plan
    background_tasks.add_task(email_service.send_welcome_email, user)
    
    verification_token = create_email_verification_token(user.email)
    background_tasks.add_task(
        email_service.send_email_verification,
        user,
        verification_token
    )
    
    return user


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Connexion utilisateur"
)
async def login(
    credentials: LoginRequest,
    db: DatabaseDep
):
    """
    Connexion utilisateur
    
    - Valide les identifiants
    - Retourne les tokens JWT (access + refresh)
    - Retourne les informations utilisateur
    """
    auth_service = AuthService(db)
    
    login_response = await auth_service.login(
        credentials.email,
        credentials.password
    )
    
    return login_response


@router.post(
    "/login/oauth2",
    response_model=LoginResponse,
    summary="Connexion OAuth2 (compatible avec FastAPI docs)"
)
async def login_oauth2(
    form_data: OAuth2PasswordRequestForm,
    db: DatabaseDep
):
    """
    Connexion OAuth2 pour la documentation FastAPI interactive
    
    Utilise le format OAuth2PasswordRequestForm pour compatibilité
    avec l'interface Swagger UI
    """
    auth_service = AuthService(db)
    
    login_response = await auth_service.login(
        form_data.username,  # Username = email
        form_data.password
    )
    
    return login_response


@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    summary="Rafraîchir le token d'accès"
)
async def refresh_token(
    token_data: RefreshTokenRequest,
    db: DatabaseDep
):
    """
    Rafraîchit le token d'accès
    
    - Prend un refresh token valide
    - Retourne un nouveau access token
    """
    auth_service = AuthService(db)
    
    response = await auth_service.refresh_access_token(token_data.refresh_token)
    
    return response


@router.post(
    "/logout",
    response_model=LogoutResponse,
    summary="Déconnexion"
)
async def logout(current_user: CurrentUser):
    """
    Déconnexion utilisateur
    
    Note: Avec JWT, la déconnexion côté client consiste à
    supprimer les tokens. Cette route existe pour la cohérence de l'API.
    """
    return LogoutResponse(message="Déconnexion réussie")


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Profil utilisateur actuel"
)
async def get_current_user_profile(current_user: CurrentUser):
    """
    Récupère le profil de l'utilisateur connecté
    
    Nécessite un token JWT valide
    """
    return current_user


@router.post(
    "/verify-email/request",
    response_model=AuthSuccessResponse,
    summary="Demander vérification email"
)
async def request_email_verification(
    request: EmailVerificationRequest,
    background_tasks: BackgroundTasks,
    db: DatabaseDep
):
    """
    Demande un email de vérification
    
    Envoie un lien de vérification à l'email spécifié
    """
    auth_service = AuthService(db)
    email_service = EmailService()
    
    user = await auth_service.get_user_by_email(request.email)
    
    if user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email déjà vérifié"
        )
    
    verification_token = create_email_verification_token(user.email)
    
    background_tasks.add_task(
        email_service.send_email_verification,
        user,
        verification_token
    )
    
    return AuthSuccessResponse(
        message="Email de vérification envoyé"
    )


@router.post(
    "/verify-email/confirm",
    response_model=AuthSuccessResponse,
    summary="Confirmer vérification email"
)
async def confirm_email_verification(
    confirmation: EmailVerificationConfirm,
    db: DatabaseDep
):
    """
    Confirme la vérification de l'email
    
    Valide le token et marque l'email comme vérifié
    """
    auth_service = AuthService(db)
    
    await auth_service.verify_email(confirmation.token)
    
    return AuthSuccessResponse(
        message="Email vérifié avec succès"
    )


@router.post(
    "/password-reset/request",
    response_model=AuthSuccessResponse,
    summary="Demander réinitialisation mot de passe"
)
async def request_password_reset(
    request: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: DatabaseDep
):
    """
    Demande de réinitialisation de mot de passe
    
    Envoie un email avec un lien de réinitialisation
    """
    auth_service = AuthService(db)
    email_service = EmailService()
    
    try:
        user = await auth_service.get_user_by_email(request.email)
        reset_token = create_password_reset_token(user.email)
        
        background_tasks.add_task(
            email_service.send_password_reset,
            user,
            reset_token
        )
    except:
        # Ne pas révéler si l'email existe (sécurité)
        pass
    
    return AuthSuccessResponse(
        message="Si cet email existe, un lien de réinitialisation a été envoyé"
    )


@router.post(
    "/password-reset/confirm",
    response_model=AuthSuccessResponse,
    summary="Confirmer réinitialisation mot de passe"
)
async def confirm_password_reset(
    confirmation: PasswordResetConfirm,
    db: DatabaseDep
):
    """
    Réinitialise le mot de passe
    
    Valide le token et définit le nouveau mot de passe
    """
    auth_service = AuthService(db)
    
    await auth_service.reset_password(
        confirmation.token,
        confirmation.new_password
    )
    
    return AuthSuccessResponse(
        message="Mot de passe réinitialisé avec succès"
    )


@router.post(
    "/password/change",
    response_model=AuthSuccessResponse,
    summary="Changer le mot de passe"
)
async def change_password(
    password_data: UserUpdatePassword,
    current_user: CurrentUser,
    db: DatabaseDep
):
    """
    Change le mot de passe de l'utilisateur connecté
    
    Nécessite le mot de passe actuel pour validation
    """
    auth_service = AuthService(db)
    
    await auth_service.change_password(
        current_user.id,
        password_data.current_password,
        password_data.new_password
    )
    
    return AuthSuccessResponse(
        message="Mot de passe modifié avec succès"
    )