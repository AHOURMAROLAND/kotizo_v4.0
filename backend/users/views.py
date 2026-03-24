import random
from datetime import timedelta
from django.utils import timezone
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, OTPToken
from .serializers import (
    InscriptionSerializer, VerifierOTPSerializer,
    ConnexionSerializer, UserProfileSerializer, UpdateThemeSerializer
)
from core.logger import get_logger

logger = get_logger()


def get_location_from_ip(ip):
    try:
        import requests as req
        r = req.get(f"http://ip-api.com/json/{ip}?lang=fr", timeout=3)
        data = r.json()
        if data.get('status') == 'success':
            return {
                'ville': data.get('city', ''),
                'pays': data.get('country', ''),
                'pays_code': data.get('countryCode', ''),
                'latitude': data.get('lat'),
                'longitude': data.get('lon'),
            }
    except Exception:
        pass
    return None


class InscriptionView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = InscriptionSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            logger.info(f"Nouvelle inscription: {user.numero_telephone}")
            return Response({'message': 'Compte créé. Vérifiez votre OTP.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifierOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifierOTPSerializer(data=request.data)
        if serializer.is_valid():
            otp = serializer.validated_data['otp']
            otp.est_utilise = True
            otp.save()
            if otp.user:
                otp.user.est_verifie = True
                otp.user.save()
            return Response({'message': 'Compte vérifié avec succès.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConnexionView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ConnexionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        numero = serializer.validated_data['numero_telephone']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(numero_telephone=numero)
        except User.DoesNotExist:
            return Response({'error': 'Identifiants incorrects.'}, status=status.HTTP_401_UNAUTHORIZED)

        user.debloquer_si_expire()

        if user.est_bloque:
            return Response({'error': 'Compte bloqué pour 12h.'}, status=status.HTTP_403_FORBIDDEN)

        if not user.check_password(password):
            user.tentatives_connexion += 1
            if user.tentatives_connexion >= 3:
                user.est_bloque = True
                user.date_blocage = timezone.now()
            user.save()
            return Response({'error': 'Identifiants incorrects.'}, status=status.HTTP_401_UNAUTHORIZED)

        user.tentatives_connexion = 0

        # Géolocalisation par IP
        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
        if ip:
            ip = ip.split(',')[0].strip()
            location = get_location_from_ip(ip)
            if location:
                user.derniere_ip = ip
                user.ville = location['ville']
                user.pays = location['pays']
                user.pays_code = location['pays_code']
                user.latitude = location['latitude']
                user.longitude = location['longitude']

        user.save()

        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserProfileSerializer(user).data
        })


class ProfilView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user


class UpdateThemeView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        serializer = UpdateThemeSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'theme': serializer.validated_data['theme']})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SoumettreVerificationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        cni_recto = request.FILES.get('cni_recto')
        cni_verso = request.FILES.get('cni_verso')
        if not cni_recto or not cni_verso:
            return Response(
                {'error': 'Les deux faces de la CNI sont requises.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.cni_recto = cni_recto
        user.cni_verso = cni_verso
        user.cni_statut = 'en_attente'
        user.save()
        return Response({'message': 'Documents soumis. En attente de validation.'})