from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import timedelta

class User(AbstractUser):
    contact = models.CharField(max_length=15, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    house_name = models.CharField(max_length=100, null=True, blank=True)
    postal_code = models.CharField(max_length=10, null=True, blank=True)

    ROLE_CHOICES = [
        (1, 'customer'),
        (2, 'admin')
    ]
    
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, default=1)

    @property
    def profile_completed(self):
        return all([self.city, self.house_name, self.contact, self.postal_code])

    def __str__(self):
        return self.username

class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.CharField(max_length=100, unique=True)
    expiry = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = get_random_string(length=32)
        if not self.expiry:
            self.expiry = timezone.now() + timedelta(minutes=15)
        super().save(*args, **kwargs)

    def is_valid(self):
        return self.expiry > timezone.now()

    def __str__(self):
        return f"Token for {self.user.username} expires at {self.expiry}"
    
class Category(models.Model):
    id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=255, unique=True)
    category_image = models.ImageField(upload_to='category_images/', null=True, blank=True)

    def __str__(self):
        return self.category_name

    @property
    def image_url(self):
        if self.category_image and hasattr(self.category_image, 'url'):
            return self.category_image.url
        return None

class Subcategory(models.Model):
    subcategory_id = models.AutoField(primary_key=True)
    subcategory_name = models.CharField(max_length=30, null=False)
    subcategory_description = models.CharField(max_length=500, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    status = models.IntegerField(null=False, default=1)

    def __str__(self):
        return f"{self.category.category_name} - {self.subcategory_name}"

    def save(self, *args, **kwargs):
        self.updated_date = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Subcategory"
        verbose_name_plural = "Subcategories"
        # Remove any unique constraints or indexes that might cause issues with MariaDB
        indexes = []
        constraints = []
        
class Cattle(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE)
    dob = models.DateField()
    weight = models.DecimalField(max_digits=6, decimal_places=2)
    color = models.CharField(max_length=50)
    image = models.ImageField(upload_to='cattle_images/')
    number_of_cattle = models.PositiveIntegerField()
    milk_production = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.category} - {self.subcategory} ({self.number_of_cattle})"

    class Meta:
        verbose_name = "Cattle"
        verbose_name_plural = "Cattle"
