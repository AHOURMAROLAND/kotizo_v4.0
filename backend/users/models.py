import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, numero_telephone, password=None, **extra_fields):
        if not numero_telephone:
            raise ValueError('Le numéro de téléphone est obligatoire')
        user = self.model(numero_telephone=numero_telephone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, numero_telephone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('est_verifie', True)
        return self.create_user(numero_telephone, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    NIVEAU_CHOICES = [
        ('basique', 'Basique'),
        ('verifie', 'Vérifié'),
        ('business', 'Business'),
    ]
    THEME_CHOICES = [
        ('vert', 'Vert Afrique'),
        ('violet', 'Violet Premium'),
        ('bleu', 'Bleu Classic'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero_telephone = models.CharField(max_length=20, unique=True)
    numero_whatsapp = models.CharField(max_length=20, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    pseudo = models.CharField(max_length=50, unique=True, null=True, blank=True)
    photo_profil = models.ImageField(upload_to='profils/', null=True, blank=True)
    niveau = models.CharField(max_length=20, choices=NIVEAU_CHOICES, default='basique')
    theme = models.CharField(max_length=20, choices=THEME_CHOICES, default='vert')

    # Vérification
    est_verifie = models.BooleanField(default=False)
    cni_recto = models.ImageField(upload_to='cni/', null=True, blank=True)
    cni_verso = models.ImageField(upload_to='cni/', null=True, blank=True)
    cni_statut = models.CharField(max_length=20, default='non_soumis')
    cni_prix = models.IntegerField(default=1000)

    # Sécurité
    est_actif = models.BooleanField(default=True)
    est_bloque = models.BooleanField(default=False)
    date_blocage = models.DateTimeField(null=True, blank=True)
    tentatives_connexion = models.IntegerField(default=0)
    appareil_token = models.CharField(max_length=255, blank=True)

    # Mobile Money
    numero_mobile_money = models.CharField(max_length=20, blank=True)
    operateur_mobile_money = models.CharField(max_length=20, blank=True)

    # Parrainage
    code_parrainage = models.CharField(max_length=10, unique=True, null=True, blank=True)
    parrain = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='filleuls')

    # Django
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'numero_telephone'
    REQUIRED_FIELDS = ['nom', 'prenom']

    class Meta:
        db_table = 'users'
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.numero_telephone})"

    def debloquer_si_expire(self):
        if self.est_bloque and self.date_blocage:
            from datetime import timedelta
            if timezone.now() > self.date_blocage + timedelta(hours=12):
                self.est_bloque = False
                self.tentatives_connexion = 0
                self.date_blocage = None
                self.save()


class StaffPermission(models.Model):
    SECTION_CHOICES = [
        ('dashboard', 'Dashboard'),
        ('users', 'Utilisateurs'),
        ('verifications', 'Vérifications'),
        ('transactions', 'Transactions'),
        ('remboursements', 'Remboursements'),
        ('alertes', 'Alertes'),
        ('sanctions', 'Sanctions'),
        ('tickets', 'Tickets'),
        ('notifications', 'Notifications'),
        ('whatsapp', 'WhatsApp'),
        ('configuration', 'Configuration'),
        ('statistics', 'Statistics'),
        ('staff', 'Staff'),
    ]
    LEVEL_CHOICES = [
        ('read', 'Lecture seule'),
        ('write', 'Lecture + Écriture'),
        ('full', 'Accès complet'),
    ]

    staff_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='staff_permissions')
    section = models.CharField(max_length=50, choices=SECTION_CHOICES)
    permission_level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='read')
    actif = models.BooleanField(default=True)
    cree_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='staff_crees')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'staff_permissions'
        unique_together = ('staff_user', 'section')

    def __str__(self):
        return f"{self.staff_user} — {self.section} ({self.permission_level})"


class OTPToken(models.Model):
    CANAL_CHOICES = [('email', 'Email'), ('whatsapp', 'WhatsApp')]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otp_tokens', null=True, blank=True)
    numero_telephone = models.CharField(max_length=20)
    email = models.EmailField(null=True, blank=True)
    code = models.CharField(max_length=6)
    canal = models.CharField(max_length=20, choices=CANAL_CHOICES)
    est_utilise = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'otp_tokens'

    def est_valide(self):
        from django.utils import timezone
        return not self.est_utilise and timezone.now() < self.expires_at