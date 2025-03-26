from django.db import models

class PermissionCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=30, blank=True)
    
    class Meta:
        verbose_name_plural = "Permission Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class CustomUserPermission(models.Model):
    
    codename = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(
        PermissionCategory,
        on_delete=models.CASCADE,
        related_name='permissions',

    )
    class Meta:
        indexes = [
            models.Index(fields=['codename']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['category', 'codename'],
                name='unique_permission_per_category'
            )
        ]
        ordering = ['category', 'codename']

    def __str__(self):
        return f"{self.category}.{self.codename}"
