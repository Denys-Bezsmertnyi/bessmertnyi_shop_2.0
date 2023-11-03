from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    money = models.DecimalField(max_digits=10, decimal_places=2, default=10000)


class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_purchases")
    product = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="user_products")
    product_quantity = models.PositiveIntegerField()
    purchase_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product} by {self.user} bought time {self.purchase_created}"


class Refund(models.Model):
    refund_time = models.DateTimeField(auto_now_add=True)
    refund_purchase = models.OneToOneField("Purchase", on_delete=models.CASCADE, related_name="refund")

    def __str__(self):
        return f"New refund, time {self.refund_time} item {self.refund_purchase}"


class Product(models.Model):
    image = models.ImageField(upload_to='product_images/',default='product_images/default_image.jpg')
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()


    def __str__(self):
        return self.title

#completed