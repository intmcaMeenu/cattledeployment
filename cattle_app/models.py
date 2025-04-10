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
    
    milk_production = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    description = models.CharField(max_length=500, null=True, blank=True)
    price = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    STATUS_CHOICES = (
        (0, 'Pending'),
        (1, 'Approved'),
        (2, 'Rejected'),
        (3, 'Sold'),  # Add this new status
    )
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    reject_message = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.category} - {self.subcategory}"

    class Meta:
        verbose_name = "Cattle"
        verbose_name_plural = "Cattle"
        
        
class VaccinationCenter(models.Model):
    center_id = models.AutoField(primary_key=True)
    
    center_name = models.CharField(max_length=50, null=False)
    center_email = models.CharField(max_length=50, null=False)
    place = models.TextField(max_length=50, null=True, blank=True)
    contact_number = models.CharField(max_length=15, null=True, blank=True)
    password = models.CharField(max_length=100, null=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    status = models.IntegerField(null=False, default=1)

    def __str__(self):
        return self.center_name

    class Meta:
        verbose_name = "Vaccination Center"
        verbose_name_plural = "Vaccination Centers"
        # Remove any unique constraints or indexes that might cause issues with MariaDB
        indexes = []
        constraints = []
        
        
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user.username}"
    def get_total_price(self):
        total = sum(item.price * item.quantity for item in self.items.all())  # Assuming you have an items relationship
        return total

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    cattle = models.ForeignKey(Cattle, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.cattle.subcategory.subcategory_name}"

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cattle = models.ForeignKey(Cattle, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.cattle.subcategory.subcategory_name} - {self.added_at}"

class Payment(models.Model):
    payment_id = models.CharField(max_length=50, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cattle = models.ForeignKey(Cattle, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=10, choices=[('success', 'Success'), ('failed', 'Failed')], default='success')

    def __str__(self):
        return f"Payment of {self.user.username} for cattle {self.cattle.id} on {self.payment_date}"

class Vaccine(models.Model):
    vaccine_id = models.AutoField(primary_key=True)
    vaccine_name = models.CharField(max_length=50, null=False)
    manufacturer = models.CharField(max_length=50, null=False)
    batch_number = models.CharField(max_length=20, null=False)
    expiry_date = models.DateField(null=False)
    center = models.ForeignKey(VaccinationCenter, on_delete=models.CASCADE)
    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    status = models.IntegerField(null=False)

    class Meta:
        indexes = []
        constraints = []

    def __str__(self):
        return self.vaccine_name
    
class Order(models.Model):
    id = models.AutoField(primary_key=True)
    order_date = models.DateField(auto_now_add=True)
    order_time = models.TimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Pending')  # You can define your own statuses
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Order {self.id} by {self.user.username} on {self.order_date}"

class OrderDetails(models.Model):
    id = models.AutoField(primary_key=True)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    quantity = models.PositiveIntegerField()
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_details')
    cattle = models.ForeignKey(Cattle, on_delete=models.CASCADE)

    def __str__(self):
        return f"OrderDetail {self.id} for Order {self.order.id}"  
    

