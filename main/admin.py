from django.contrib import admin
from .models import Product,User,Refund,Purchase

admin.site.register(Product)
admin.site.register(User)
admin.site.register(Refund)
admin.site.register(Purchase)
