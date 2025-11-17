# apps/users/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

# Tu modelo User se mantiene igual
class User(AbstractUser):
    class Rol(models.TextChoices):
        GUARDIA = "GUARDIA", "Guardia"
        MECANICO = "MECANICO", "Mecánico"
        SUPERVISOR = "SUPERVISOR", "Supervisor"
        SPONSOR = "SPONSOR", "Sponsor"
        ADMIN = "ADMIN", "Administrador"

    rol = models.CharField(max_length=20, choices=Rol.choices, default=Rol.ADMIN)
    email = models.EmailField(unique=True)
    REQUIRED_FIELDS = ['email'] # Le dice a Django que el email es obligatorio

# === AÑADIMOS EL MODELO PROFILE ===
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=32, blank=True)  # <--- NUEVO

    def __str__(self):
        return self.user.username


# === AÑADIMOS LA SEÑAL PARA CREAR EL PERFIL AUTOMÁTICAMENTE ===
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """Crea un Profile automáticamente cuando se crea un nuevo User."""
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    """Guarda el Profile automáticamente cuando se guarda el User."""
    instance.profile.save()


@receiver(post_save, sender=User)
def ensure_user_profile(sender, instance, created, **kwargs):
    # Crea el perfil si no existe (idempotente)
    Profile.objects.get_or_create(
        user=instance,
        defaults={
            "first_name": instance.first_name or "",
            "last_name": instance.last_name or "",
            # "phone_number": ""  # si quieres default explícito
        }
    )
    # Si quieres sincronizar nombres cada vez que cambien en User:
    Profile.objects.filter(user=instance).update(
        first_name=instance.first_name or "",
        last_name=instance.last_name or "",
    )
