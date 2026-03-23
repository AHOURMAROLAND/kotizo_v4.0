import re
import random
import string
from django.conf import settings

def calculer_frais(montant: float) -> dict:
    frais_total = montant * (settings.KOTIZO_FRAIS_PERCENT / 100)
    gain_kotizo = montant * (settings.KOTIZO_GAIN_PERCENT / 100)
    payin = montant * 0.02
    payout = montant * 0.025
    return {
        'montant_brut': montant,
        'frais_total': round(frais_total, 2),
        'gain_kotizo': round(gain_kotizo, 2),
        'payin': round(payin, 2),
        'payout': round(payout, 2),
        'montant_net': round(montant - gain_kotizo, 2),
    }

def detecter_operateur(numero: str) -> str:
    numero = re.sub(r'\D', '', numero)
    if numero.startswith('228'):
        numero = numero[3:]
    moov = ('90','91','92','93','94','95','96','97','98','99','70','71','72','73','74','75','76','77','78','79')
    tmoney = ('22','23','24','25','26','27','28','29')
    if numero[:2] in moov:
        return 'moov'
    if numero[:2] in tmoney:
        return 'tmoney'
    return 'inconnu'

def generer_code(longueur: int = 12) -> str:
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=longueur))

def masquer_numero(numero: str) -> str:
    if len(numero) < 4:
        return '****'
    return numero[:3] + '****' + numero[-2:]

def formater_montant(montant: float) -> str:
    return f"{int(montant):,} FCFA".replace(',', ' ')