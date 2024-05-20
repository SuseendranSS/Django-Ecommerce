from django.db import models
from base.models import BaseModel
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
from base.emails import send_account_activation_email
from products.models import *


class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    is_email_verified = models.BooleanField(default=False)
    email_token = models.CharField(max_length=100, null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile')

    def get_cart_count(self):
        try:
            temp = CartItems.objects.filter(cart__is_paid=False, cart__user=self.user).count()
            return temp
        except Exception as e:
            print("Exception:", e)  # Add this line for debugging
            return 0 
    
class Cart(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    razorpay_order_id = models.CharField(max_length = 100, null = True, blank = True)
    razorpay_payment_id = models.CharField(max_length = 100, null = True, blank = True)
    razorpay_payment_signature = models.CharField(max_length = 100, null = True, blank = True)

    def get_cart_total(self):
        cart_items = self.cart_items.all()
        total_price = sum(item.get_total_price() for item in cart_items)
        return total_price

class CartItems(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(product, on_delete=models.SET_NULL, null=True, blank=True)
    color_variant = models.ForeignKey(ColorVariant, on_delete=models.SET_NULL, null=True, blank=True)
    size_variant = models.ForeignKey(SizeVariant, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)

    def get_total_price(self):
        price = self.product.price

        # Add prices of color and size variants if they exist
        if self.color_variant:
            price += self.color_variant.price
        if self.size_variant:
            price += self.size_variant.price
        
        return price * self.quantity

    @property
    def product_slug(self):
        # Access the product's slug through the product relationship
        if self.product:
            return self.product.slug
        else:
            return None

@receiver(post_save, sender=User)
def send_email_token(sender,instance,created, **kwargs):
    try:
        if created:
            email_token = str(uuid.uuid4())
            Profile.objects.create(user = instance , email_token = email_token)
            email = instance.email
            send_account_activation_email(email, email_token)
    except Exception as e:
        print(e)
