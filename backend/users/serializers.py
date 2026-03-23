import random
from django.utils import timezone
from datetime import timedelta
from rest_framework import serializers
from .models import User, OTPToken
from core.utils import generer_code

class InscriptionSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    canal_otp = serializers.ChoiceField(choices=['email', 'whatsapp'])

    class Meta:
        model = User
        fields = ['numero_telephone', 'numero_whatsapp', 'email', 'nom', 'prenom', 'password', 'canal_otp']

    def validate_numero_telephone(self, value):
        if User.objects.filter(numero_telephone=value).exists():
            raise serializers.ValidationError("Ce numéro est déjà utilisé.")
        return value

    def create(self, validated_data):
        canal = validated_data.pop('canal_otp')
        user = User.objects.create_user(**validated_data)
        self._envoyer_otp(user, canal)
        return user

    def _envoyer_otp(self, user, canal):
        code = str(random.randint(100000, 999999))
        OTPToken.objects.create(
            user=user,
            numero_telephone=user.numero_telephone,
            email=user.email,
            code=code,
            canal=canal,
            expires_at=timezone.now() + timedelta(minutes=2)
        )
        if canal == 'whatsapp':
            from core.whatsapp import whatsapp_client
            whatsapp_client.envoyer_otp(user.numero_whatsapp or user.numero_telephone, code)
        else:
            from core.email_router import envoyer_otp_email
            envoyer_otp_email(user.email, code)


class VerifierOTPSerializer(serializers.Serializer):
    numero_telephone = serializers.CharField()
    code = serializers.CharField(max_length=6)

    def validate(self, data):
        try:
            otp = OTPToken.objects.filter(
                numero_telephone=data['numero_telephone'],
                code=data['code'],
                est_utilise=False
            ).latest('created_at')
        except OTPToken.DoesNotExist:
            raise serializers.ValidationError("Code invalide.")
        if not otp.est_valide():
            raise serializers.ValidationError("Code expiré. Veuillez recommencer.")
        data['otp'] = otp
        return data


class ConnexionSerializer(serializers.Serializer):
    numero_telephone = serializers.CharField()
    password = serializers.CharField(write_only=True)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'numero_telephone', 'numero_whatsapp', 'email',
            'nom', 'prenom', 'pseudo', 'photo_profil', 'niveau',
            'theme', 'est_verifie', 'cni_statut', 'numero_mobile_money',
            'operateur_mobile_money', 'code_parrainage', 'created_at'
        ]
        read_only_fields = ['id', 'niveau', 'est_verifie', 'cni_statut', 'created_at']


class UpdateThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['theme']