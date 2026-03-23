from django.core.mail import send_mail
from django.conf import settings
from core.logger import get_logger

logger = get_logger()

def envoyer_email(destinataire: str, sujet: str, message: str, html_message: str = None) -> bool:
    try:
        send_mail(
            subject=sujet,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[destinataire],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Email envoyé à {destinataire}")
        return True
    except Exception as e:
        logger.error(f"Erreur email {destinataire}: {str(e)}")
        return False

def envoyer_otp_email(destinataire: str, otp: str) -> bool:
    sujet = "Kotizo — Code de vérification"
    message = f"Votre code de vérification Kotizo est : {otp}\n\nValable 2 minutes."
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:400px;margin:auto;padding:20px">
        <h2 style="color:#16A34A">Kotizo</h2>
        <p>Votre code de vérification est :</p>
        <h1 style="letter-spacing:8px;color:#16A34A">{otp}</h1>
        <p style="color:#666">Valable <strong>2 minutes</strong>. Ne le partagez pas.</p>
    </div>
    """
    return envoyer_email(destinataire, sujet, message, html)

def envoyer_notification_email(destinataire: str, sujet: str, contenu: str) -> bool:
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:400px;margin:auto;padding:20px">
        <h2 style="color:#16A34A">Kotizo</h2>
        <p>{contenu}</p>
    </div>
    """
    return envoyer_email(destinataire, sujet, contenu, html)