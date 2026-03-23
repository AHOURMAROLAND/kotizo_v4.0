from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('inscription/', views.InscriptionView.as_view(), name='inscription'),
    path('verifier-otp/', views.VerifierOTPView.as_view(), name='verifier-otp'),
    path('connexion/', views.ConnexionView.as_view(), name='connexion'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('profil/', views.ProfilView.as_view(), name='profil'),
    path('profil/theme/', views.UpdateThemeView.as_view(), name='update-theme'),
    path('verification/soumettre/', views.SoumettreVerificationView.as_view(), name='soumettre-verification'),
]