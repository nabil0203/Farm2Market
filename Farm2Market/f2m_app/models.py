from django.db import models
from django.contrib.auth.models import User


# Farmer

class FarmerProfile(models.Model):
    farmer_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="farmer_profile"
    )
    farm_name = models.CharField(max_length=255)
    farm_location = models.CharField(max_length=255)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"{self.farm_name} ({self.user})"


# Buyer
class BuyerProfile(models.Model):
    buyer_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="buyer_profile"
    )
    delivery_address = models.TextField()

    def __str__(self):
        return f"Buyer Profile: {self.user}"


# Category
class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


# Product
class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    farmer = models.ForeignKey(
        FarmerProfile, on_delete=models.CASCADE, related_name="products"
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products"
    )
    name = models.CharField(max_length=255)
    description = models.TextField()
    price_per_unit = models.IntegerField(default=0)
    stock_quantity = models.IntegerField(default=0)
    unit = models.CharField(max_length=50)
    image = models.ImageField(upload_to="product_images/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# Cart
class Cart(models.Model):
    cart_id = models.AutoField(primary_key=True)
    buyer = models.OneToOneField(
        BuyerProfile, on_delete=models.CASCADE, related_name="cart"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart - {self.buyer.user.username}"


# Cart Item
class CartItem(models.Model):
    cart_item_id = models.AutoField(primary_key=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.product.price_per_unit * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Cart: {self.cart.buyer.user.username})"
