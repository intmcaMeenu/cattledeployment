from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Payment, Wishlist, CartItem

@receiver(post_save, sender=Payment)
def remove_sold_cattle(sender, instance, created, **kwargs):
    if created:  # Only run this when a new Payment is created
        sold_cattle = instance.cattle

        # Remove from all users' wishlists
        Wishlist.objects.filter(cattle=sold_cattle).delete()

        # Remove from all users' carts
        CartItem.objects.filter(cattle=sold_cattle).delete()

        # Optionally, you might want to update the Cattle status to indicate it's sold
        sold_cattle.status = 3  # Assuming 3 means 'Sold', you might need to add this to your STATUS_CHOICES
        sold_cattle.save()
