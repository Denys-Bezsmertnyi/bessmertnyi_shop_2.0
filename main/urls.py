from django.urls import path
from .views import RegisterView, Login, Logout, ProductsView, AdminProductListView, ChangeProductView, AddProductView, RefundsView, RefundAgreeView, \
    RefundRejectView, PurchaseCreateView, PurchaseListView, CreateRefund

app_name = 'main'
urlpatterns = [
    path('', ProductsView.as_view(), name="index"),
    path('register/', RegisterView.as_view(), name="register"),
    path('login/', Login.as_view(), name="login"),
    path('logout/', Logout.as_view(), name="logout"),
    path('product-list/', AdminProductListView.as_view(), name="product_list"),
    path('change-product/<int:pk>/', ChangeProductView.as_view(), name="change_product"),
    path('add-product/', AddProductView.as_view(), name="add_product"),
    path('refunds/', RefundsView.as_view(), name="refunds"),
    path('refund_agree/<int:pk>/', RefundAgreeView.as_view(), name='refund_agree'),
    path('refund_reject/<int:pk>/', RefundRejectView.as_view(), name='refund_reject'),
    path('purchase/<int:pk>/', PurchaseCreateView.as_view(), name='purchase_product'),
    path('purchase-list/', PurchaseListView.as_view(), name='purchase_list'),
    path('create-refund/<int:purchase_id>/', CreateRefund.as_view(), name='create_refund'),
]