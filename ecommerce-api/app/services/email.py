
"""
Service d'envoi d'emails
Gestion des notifications par email
"""

import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List
from jinja2 import Template

from app.core.config import settings
from app.models.user import User
from app.models.order import Order


class EmailService:
    """Service d'envoi d'emails"""
    
    def __init__(self):
        self.smtp_host = settings.MAIL_SERVER
        self.smtp_port = settings.MAIL_PORT
        self.smtp_username = settings.MAIL_USERNAME
        self.smtp_password = settings.MAIL_PASSWORD
        self.from_email = settings.MAIL_FROM
        self.from_name = settings.MAIL_FROM_NAME
        self.use_tls = settings.MAIL_TLS
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Envoie un email
        
        Args:
            to_email: Email destinataire
            subject: Sujet
            html_content: Contenu HTML
            text_content: Contenu texte (optionnel)
        
        Returns:
            True si envoyé avec succès
        """
        try:
            # Créer le message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email
            
            # Ajouter le contenu texte si fourni
            if text_content:
                part_text = MIMEText(text_content, "plain")
                message.attach(part_text)
            
            # Ajouter le contenu HTML
            part_html = MIMEText(html_content, "html")
            message.attach(part_html)
            
            # Envoyer l'email
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_username,
                password=self.smtp_password,
                use_tls=self.use_tls
            )
            
            return True
        
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email: {e}")
            return False
    
    async def send_welcome_email(self, user: User) -> bool:
        """
        Envoie un email de bienvenue
        
        Args:
            user: Utilisateur
        
        Returns:
            True si envoyé
        """
        subject = f"Bienvenue sur {settings.APP_NAME} !"
        
        html_content = f"""
        <html>
            <body>
                <h1>Bienvenue {user.first_name} !</h1>
                <p>Merci de vous être inscrit sur {settings.APP_NAME}.</p>
                <p>Nous sommes ravis de vous compter parmi nous.</p>
                <br>
                <p>Cordialement,</p>
                <p>L'équipe {settings.APP_NAME}</p>
            </body>
        </html>
        """
        
        return await self.send_email(user.email, subject, html_content)
    
    async def send_email_verification(
        self,
        user: User,
        verification_token: str
    ) -> bool:
        """
        Envoie un email de vérification
        
        Args:
            user: Utilisateur
            verification_token: Token de vérification
        
        Returns:
            True si envoyé
        """
        verification_url = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"
        
        subject = "Vérifiez votre email"
        
        html_content = f"""
        <html>
            <body>
                <h1>Vérification de votre email</h1>
                <p>Bonjour {user.first_name},</p>
                <p>Merci de vous être inscrit sur {settings.APP_NAME}.</p>
                <p>Pour activer votre compte, veuillez cliquer sur le lien ci-dessous :</p>
                <p><a href="{verification_url}">Vérifier mon email</a></p>
                <p>Ce lien est valide pendant 24 heures.</p>
                <br>
                <p>Si vous n'avez pas créé de compte, ignorez cet email.</p>
                <br>
                <p>Cordialement,</p>
                <p>L'équipe {settings.APP_NAME}</p>
            </body>
        </html>
        """
        
        return await self.send_email(user.email, subject, html_content)
    
    async def send_password_reset(
        self,
        user: User,
        reset_token: str
    ) -> bool:
        """
        Envoie un email de réinitialisation de mot de passe
        
        Args:
            user: Utilisateur
            reset_token: Token de réinitialisation
        
        Returns:
            True si envoyé
        """
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        
        subject = "Réinitialisation de votre mot de passe"
        
        html_content = f"""
        <html>
            <body>
                <h1>Réinitialisation de mot de passe</h1>
                <p>Bonjour {user.first_name},</p>
                <p>Vous avez demandé à réinitialiser votre mot de passe.</p>
                <p>Cliquez sur le lien ci-dessous pour créer un nouveau mot de passe :</p>
                <p><a href="{reset_url}">Réinitialiser mon mot de passe</a></p>
                <p>Ce lien est valide pendant 1 heure.</p>
                <br>
                <p>Si vous n'avez pas demandé cette réinitialisation, ignorez cet email.</p>
                <br>
                <p>Cordialement,</p>
                <p>L'équipe {settings.APP_NAME}</p>
            </body>
        </html>
        """
        
        return await self.send_email(user.email, subject, html_content)
    
    async def send_order_confirmation(
        self,
        user: User,
        order: Order
    ) -> bool:
        """
        Envoie une confirmation de commande
        
        Args:
            user: Utilisateur
            order: Commande
        
        Returns:
            True si envoyé
        """
        subject = f"Confirmation de commande #{order.id}"
        
        # Créer la liste des articles
        items_html = ""
        for item in order.items:
            items_html += f"""
                <tr>
                    <td>{item.product.name}</td>
                    <td>{item.quantity}</td>
                    <td>{item.unit_price}€</td>
                    <td>{item.subtotal}€</td>
                </tr>
            """
        
        html_content = f"""
        <html>
            <body>
                <h1>Confirmation de commande</h1>
                <p>Bonjour {user.first_name},</p>
                <p>Merci pour votre commande !</p>
                <br>
                <h2>Commande #{order.id}</h2>
                <p>Date: {order.created_at.strftime('%d/%m/%Y %H:%M')}</p>
                <br>
                <h3>Articles commandés :</h3>
                <table border="1" cellpadding="10">
                    <thead>
                        <tr>
                            <th>Produit</th>
                            <th>Quantité</th>
                            <th>Prix unitaire</th>
                            <th>Sous-total</th>
                        </tr>
                    </thead>
                    <tbody>
                        {items_html}
                    </tbody>
                </table>
                <br>
                <h3>Total: {order.total_amount}€</h3>
                <br>
                <p>Nous vous tiendrons informé de l'avancement de votre commande.</p>
                <br>
                <p>Cordialement,</p>
                <p>L'équipe {settings.APP_NAME}</p>
            </body>
        </html>
        """
        
        return await self.send_email(user.email, subject, html_content)
    
    async def send_order_shipped(
        self,
        user: User,
        order: Order,
        tracking_number: Optional[str] = None
    ) -> bool:
        """
        Envoie une notification d'expédition
        
        Args:
            user: Utilisateur
            order: Commande
            tracking_number: Numéro de suivi (optionnel)
        
        Returns:
            True si envoyé
        """
        subject = f"Votre commande #{order.id} a été expédiée"
        
        tracking_info = ""
        if tracking_number:
            tracking_info = f"<p>Numéro de suivi: <strong>{tracking_number}</strong></p>"
        
        html_content = f"""
        <html>
            <body>
                <h1>Commande expédiée !</h1>
                <p>Bonjour {user.first_name},</p>
                <p>Bonne nouvelle ! Votre commande #{order.id} a été expédiée.</p>
                {tracking_info}
                <p>Vous devriez la recevoir dans les prochains jours.</p>
                <br>
                <p>Cordialement,</p>
                <p>L'équipe {settings.APP_NAME}</p>
            </body>
        </html>
        """
        
        return await self.send_email(user.email, subject, html_content)
    
    async def send_order_delivered(
        self,
        user: User,
        order: Order
    ) -> bool:
        """
        Envoie une notification de livraison
        
        Args:
            user: Utilisateur
            order: Commande
        
        Returns:
            True si envoyé
        """
        subject = f"Votre commande #{order.id} a été livrée"
        
        html_content = f"""
        <html>
            <body>
                <h1>Commande livrée !</h1>
                <p>Bonjour {user.first_name},</p>
                <p>Votre commande #{order.id} a été livrée avec succès.</p>
                <p>Nous espérons que vous êtes satisfait de votre achat.</p>
                <p>N'hésitez pas à laisser un avis sur les produits commandés.</p>
                <br>
                <p>Cordialement,</p>
                <p>L'équipe {settings.APP_NAME}</p>
            </body>
        </html>
        """
        
        return await self.send_email(user.email, subject, html_content)
    
    async def send_order_cancelled(
        self,
        user: User,
        order: Order,
        reason: Optional[str] = None
    ) -> bool:
        """
        Envoie une notification d'annulation
        
        Args:
            user: Utilisateur
            order: Commande
            reason: Raison de l'annulation (optionnel)
        
        Returns:
            True si envoyé
        """
        subject = f"Votre commande #{order.id} a été annulée"
        
        reason_text = ""
        if reason:
            reason_text = f"<p>Raison: {reason}</p>"
        
        html_content = f"""
        <html>
            <body>
                <h1>Commande annulée</h1>
                <p>Bonjour {user.first_name},</p>
                <p>Votre commande #{order.id} a été annulée.</p>
                {reason_text}
                <p>Si vous avez des questions, n'hésitez pas à nous contacter.</p>
                <br>
                <p>Cordialement,</p>
                <p>L'équipe {settings.APP_NAME}</p>
            </body>
        </html>
        """
        
        return await self.send_email(user.email, subject, html_content)