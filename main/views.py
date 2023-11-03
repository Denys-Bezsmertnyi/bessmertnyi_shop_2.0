from django.contrib.auth.views import LoginView, LogoutView
from django.db import transaction
from django.urls import reverse
from django.views.generic.edit import UpdateView, DeleteView, FormView
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import CreateView, ListView, DetailView
from .forms import CustomUserCreationForm, PurchaseForm, RefundForm
from .models import Product, Refund, Purchase
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.translation import gettext as _

class IsAdminMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser


class Products(ListView):
    paginate_by = 8
    model = Product
    template_name = 'main/index.html'


class AdminProductList(IsAdminMixin, ListView):
    paginate_by = 8
    model = Product
    template_name = 'main/admin_panel/product_list.html'
    context_object_name = 'products'


class Register(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'main/user/register.html'
    success_url = '/'


class Login(LoginView):
    template_name = 'main/user/login.html'
    success_url = '/'

    def get_success_url(self):
        return self.success_url


class Logout(LoginRequiredMixin, LogoutView):
    next_page = '/'
    login_url = 'login/'


class ChangeProduct(IsAdminMixin, UpdateView):
    model = Product
    fields = ['image', 'title', 'description', 'price', 'stock']
    template_name = 'main/admin_panel/change_product.html'
    success_url = '/product-list/'


class AddProduct(IsAdminMixin, CreateView):
    template_name = 'main/admin_panel/add_product.html'
    model = Product
    fields = ['image', 'title', 'description', 'price', 'stock']
    success_url = '/product-list/'


class Refunds(IsAdminMixin, ListView):
    model = Refund
    template_name = 'main/admin_panel/refunds.html'
    paginate_by = 8


class RefundAgree(IsAdminMixin, DeleteView):
    model = Refund
    success_url = '/refunds/'

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        refund = self.get_object()
        purchase = refund.refund_purchase

        user = purchase.user
        user.money += purchase.product.price * purchase.product_quantity
        user.save()

        product = purchase.product
        product.stock += purchase.product_quantity
        product.save()

        purchase.delete()
        refund.delete()

        return redirect(self.success_url)


class RefundReject(IsAdminMixin, DeleteView):
    model = Refund
    success_url = '/refunds/'

    def post(self, request, *args, **kwargs):
        refund = self.get_object()
        refund.delete()
        return HttpResponseRedirect(self.success_url)


class ProductPurchase(DetailView, FormView):
    model = Product
    template_name = 'main/user/product_purchase.html'
    context_object_name = 'product'
    form_class = PurchaseForm
    success_url = '/'

    def form_valid(self, form):
        product = self.get_object()
        quantity = form.cleaned_data['quantity']

        if quantity <= product.stock:
            total_price = product.price * quantity
            user = self.request.user

            if user.money >= total_price:
                purchase = Purchase(user=user, product=product, product_quantity=quantity)
                purchase.save()

                product.stock -= quantity
                product.save()

                user.money -= total_price
                user.save()

                messages.success(self.request, 'Successful Purchase!')
                return HttpResponseRedirect(self.success_url)
            else:
                messages.error(self.request, 'Not Enough money')
        else:
            messages.error(self.request, 'We dont have that much in stock')

        return super().form_valid(form)

class PurchaseList(LoginRequiredMixin, ListView):
    model = Purchase
    template_name = 'main/user/purchase_list.html'
    context_object_name = 'purchases'

    def get_queryset(self):
        return Purchase.objects.filter(user=self.request.user)


class CreateRefund(CreateView):
    model = Refund
    form_class = RefundForm
    success_url = '/purchase-list/'

    def form_valid(self, form):
        purchase_id = self.kwargs['purchase_id']
        purchase = Purchase.objects.get(pk=purchase_id)

        from datetime import timedelta
        from django.utils import timezone
        now = timezone.now()
        if now - purchase.purchase_created > timedelta(minutes=1):
            messages.success(self.request, "Timer has been expired, you have 1 minute to create refund request")
            return HttpResponseRedirect(reverse('main:purchase_list'))

        refund = form.save(commit=False)
        refund.refund_purchase = purchase
        refund.save()

        return super().form_valid(form)


# completed
