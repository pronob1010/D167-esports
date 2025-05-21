from django.db import models
from Accounts.models import User

class Tenant(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, help_text="Unique identifier for URLs")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_tenants")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
