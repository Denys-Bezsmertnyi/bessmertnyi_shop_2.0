from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import CreateView, ListView
from django.views.generic.edit import UpdateView, DeleteView

from main.forms import CustomUserCreationForm, PurchaseForm, RefundForm
from main.mixins import AdminRequiredMixin
from main.models import Product, Refund, Purchase


class ProductsView(ListView):
    paginate_by = 8
    model = Product
    template_name = 'main/index.html'
    extra_context = {'purchase_form': PurchaseForm}


class AdminProductListView(AdminRequiredMixin, ListView):
    paginate_by = 8
    model = Product
    template_name = 'main/admin_panel/product_list.html'
    context_object_name = 'products'


class RegisterView(CreateView):
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


class ChangeProductView(AdminRequiredMixin, UpdateView):
    model = Product
    fields = ['image', 'title', 'description', 'price', 'stock']
    template_name = 'main/admin_panel/change_product.html'
    success_url = '/product-list/'


class AddProductView(AdminRequiredMixin, CreateView):
    template_name = 'main/admin_panel/add_product.html'
    model = Product
    fields = ['image', 'title', 'description', 'price', 'stock']
    success_url = '/product-list/'


class RefundsView(AdminRequiredMixin, ListView):
    model = Refund
    template_name = 'main/admin_panel/refunds.html'
    paginate_by = 8


class RefundAgreeView(AdminRequiredMixin, DeleteView):
    model = Refund
    success_url = '/refunds/'

    def form_valid(self, form):
        user = self.object.refund_purchase.user
        user.money += self.object.refund_purchase.product.price * self.object.refund_purchase.product_quantity
        product = self.object.refund_purchase.product
        product.stock += self.object.refund_purchase.product_quantity
        with transaction.atomic():
            user.save()
            product.save()
            self.object.refund_purchase.delete()
            return super().form_valid(form=form)


class RefundRejectView(AdminRequiredMixin, DeleteView):
    model = Refund
    success_url = '/refunds/'


class PurchaseCreateView(LoginRequiredMixin, CreateView):
    model = Purchase
    form_class = PurchaseForm
    success_url = '/'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"request": self.request, "product_pk": self.kwargs.get('pk')})
        return kwargs

    def form_invalid(self, form):
        return HttpResponseRedirect(reverse('main:index'))

    def form_valid(self, form):
        product = form.product
        quantity = form.cleaned_data.get('product_quantity')
        total_price = product.price * quantity
        purchase = form.save(commit=False)
        purchase.product = product
        purchase.user = self.request.user
        product.stock -= quantity
        self.request.user.money -= total_price
        with transaction.atomic():
            purchase.save()
            product.save()
            self.request.user.save()
        messages.success(self.request, 'Successful Purchase!')
        return super().form_valid(form)


class PurchaseListView(LoginRequiredMixin, ListView):
    model = Purchase
    template_name = 'main/user/purchase_list.html'
    context_object_name = 'purchases'

    def get_queryset(self):
        return Purchase.objects.filter(user=self.request.user, refund__isnull=True,
                                       purchase_created__gt=timezone.now() - timedelta(
                                           seconds=settings.LIMIT_TIME_TO_REFUND))


class CreateRefund(CreateView):
    model = Refund
    form_class = RefundForm
    success_url = '/purchase-list/'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"request": self.request, "purchase_id": self.kwargs.get('purchase_id')})
        return kwargs

    def form_valid(self, form):
        refund = form.save(commit=False)
        refund.refund_purchase = form.purchase
        refund.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        return HttpResponseRedirect(reverse('main:purchase_list'))
