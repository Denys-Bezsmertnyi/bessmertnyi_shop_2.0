from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Purchase, Refund


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']


class PurchaseForm(forms.Form):
    quantity = forms.IntegerField(
        label='Quantity',
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        min_value=1
    )

class RefundForm(forms.ModelForm):
    class Meta:
        model = Refund
        fields = []