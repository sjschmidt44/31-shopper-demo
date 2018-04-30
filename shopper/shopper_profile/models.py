from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver


class ActiveShopperProfileManager(models.Manager):
    """Custom manager for only active profiles."""

    def get_queryset(self):
        """Limit the queryset to only profiles with active users."""
        all_profiles = super(ActiveShopperProfileManager, self).get_queryset()
        return all_profiles.filter(user__is_active=True)


class ShopperProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    street = models.CharField(max_length=1024, null=True, blank=True)
    city = models.CharField(max_length=1024, null=True, blank=True)
    state = models.CharField(max_length=2, null=True, blank=True)
    zip_code = models.CharField(max_length=12, null=True, blank=True)
    cell = models.CharField(max_length=20, null=True, blank=True)
    home = models.CharField(max_length=20, null=True, blank=True)

    @property
    def is_active(self):
        """Whether the User of the profile is active or not."""
        return self.user.is_active

    objects = models.Manager()
    active = ActiveShopperProfileManager()

    def __str__(self):
        return self.user.username


@receiver(models.signals.post_save, sender=User)
def create_profile(sender, **kwargs):
    if kwargs['created']:
        profile = ShopperProfile(user=kwargs['instance'])
        profile.save()
