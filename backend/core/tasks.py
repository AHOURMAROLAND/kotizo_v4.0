from celery import shared_task
from core.logger import get_logger

logger = get_logger()

@shared_task
def detection_fraude():
    from users.models import User
    from paiements.models import Transaction
    from django.utils import timezone
    from datetime import timedelta

    seuil = timezone.now() - timedelta(hours=1)
    users_suspects = []

    for user in User.objects.filter(est_actif=True):
        nb_transactions = Transaction.objects.filter(
            user=user,
            created_at__gte=seuil,
            statut='completed'
        ).count()
        if nb_transactions > 20:
            users_suspects.append(user.id)
            logger.warning(f"Fraude potentielle détectée: user {user.id} — {nb_transactions} transactions/heure")

    return {'suspects': users_suspects}

@shared_task
def envoyer_notification_async(user_id: int, message: str, canal: str = 'whatsapp'):
    from users.models import User
    from core.whatsapp import whatsapp_client
    from core.email_router import envoyer_notification_email

    try:
        user = User.objects.get(id=user_id)
        if canal == 'whatsapp' and user.numero_whatsapp:
            whatsapp_client.envoyer_notification(user.numero_whatsapp, message)
        elif canal == 'email' and user.email:
            envoyer_notification_email(user.email, "Kotizo — Notification", message)
    except Exception as e:
        logger.error(f"Erreur notification async user {user_id}: {str(e)}")