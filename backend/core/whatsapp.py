import requests
import time
from django.conf import settings
from core.logger import get_logger

logger = get_logger()

class EvolutionAPIClient:
    def __init__(self):
        self.base_url = settings.EVOLUTION_API_URL
        self.api_key = settings.EVOLUTION_API_KEY
        self.instance = settings.EVOLUTION_INSTANCE
        self.headers = {
            'apikey': self.api_key,
            'Content-Type': 'application/json',
        }

    def envoyer_message(self, numero: str, message: str, delay: int = 1500) -> dict:
        try:
            time.sleep(delay / 1000)
            url = f"{self.base_url}/message/sendText/{self.instance}"
            payload = {
                'number': numero,
                'text': message,
                'delay': delay,
            }
            response = requests.post(url, json=payload, headers=self.headers, timeout=10)
            response.raise_for_status()
            logger.info(f"WhatsApp envoyé à {numero}")
            return {'success': True, 'data': response.json()}
        except Exception as e:
            logger.error(f"Erreur WhatsApp {numero}: {str(e)}")
            return {'success': False, 'error': str(e)}

    def envoyer_otp(self, numero: str, otp: str) -> dict:
        message = f"*Kotizo* - Votre code de vérification est : *{otp}*\n\nValable 2 minutes. Ne le partagez pas."
        return self.envoyer_message(numero, message)

    def envoyer_notification(self, numero: str, texte: str) -> dict:
        message = f"*Kotizo* 🔔\n\n{texte}"
        return self.envoyer_message(numero, message)


whatsapp_client = EvolutionAPIClient()