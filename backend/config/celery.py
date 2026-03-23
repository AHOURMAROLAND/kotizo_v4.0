import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('kotizo')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    # Vérifier les cotisations expirées toutes les heures
    'check-cotisations-expirees': {
        'task': 'cotisations.tasks.check_cotisations_expirees',
        'schedule': crontab(minute=0, hour='*'),
    },
    # Alerte 12h avant expiration cotisation
    'alert-cotisations-proche-expiration': {
        'task': 'cotisations.tasks.alert_proche_expiration',
        'schedule': crontab(minute=0, hour='*'),
    },
    # Vérifier les Quick Pay expirés toutes les 5 minutes
    'check-quickpay-expires': {
        'task': 'quickpay.tasks.check_quickpay_expires',
        'schedule': crontab(minute='*/5'),
    },
    # Rapport journalier à 20h
    'rapport-journalier': {
        'task': 'admin_panel.tasks.rapport_journalier',
        'schedule': crontab(minute=0, hour=20),
    },
    # Détection fraude toutes les 30 minutes
    'detection-fraude': {
        'task': 'core.tasks.detection_fraude',
        'schedule': crontab(minute='*/30'),
    },
}

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')