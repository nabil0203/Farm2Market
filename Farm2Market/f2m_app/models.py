from django.db import models
from django.conf import settings



class FarmerProfile(models.Model):
    farmer_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="farmer_profile",
    )
    farm_name = models.CharField(max_length=255)
    farm_location = models.CharField(max_length=255)
    bio = models.TextField(blank=True)

    class Meta:
        ordering = ["farm_name"]

    def __str__(self):
        return f"{self.farm_name} ({self.user})"


# Category
class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

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
    price_per_unit = models.FloatField()
    stock_quantity = models.IntegerField()
    unit = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


# Buyer
class BuyerProfile(models.Model):
    buyer_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="buyer_profile"
    )
    delivery_address = models.TextField()

    class Meta:
        ordering = ["buyer_id"]

    def __str__(self):
        return f"Buyer Profile: {self.user}"
