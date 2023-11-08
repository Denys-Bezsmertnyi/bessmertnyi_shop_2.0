from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import User, Refund, Purchase, Product


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']


class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['product_quantity', ]

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.product_pk = kwargs.pop('product_pk', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        try:
            product = Product.objects.get(pk=self.product_pk)
            self.product = product
        except Product.DoesNotExist:
            messages.error(self.request, "Incorrect product id")
            raise ValidationError("Incorrect product id")
        quantity = cleaned_data['product_quantity']
        if product.stock < quantity:
            messages.error(self.request, "Not enough products in stock")
            self.add_error("product_quantity", "Not enough products in stock")
        if quantity * product.price > self.request.user.money:
            messages.error(self.request, "Not enough money")
            self.add_error(None, "Not enough money")




class RefundForm(forms.ModelForm):
    class Meta:
        model = Refund
        fields = []

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.purchase_id = kwargs.pop('purchase_id', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        try:
            purchase = Purchase.objects.get(pk=self.purchase_id)
            if hasattr(purchase, "refund"):
                messages.error(self.request, "Refund request exists")
                raise ValidationError('Refund request exists')
            if (timezone.now() - purchase.purchase_created).seconds > settings.LIMIT_TIME_TO_REFUND:
                messages.error(self.request, "Timer has been expired, you have 1 minute to create refund request")
                raise ValidationError("Timer has been expired, you have 1 minute to create refund request")
            self.purchase = purchase
        except Purchase.DoesNotExist:
            messages.error(self.request, "Incorrect purchase id")
            raise ValidationError("Incorrect purchase id")