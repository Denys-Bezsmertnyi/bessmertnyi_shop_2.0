from django.urls import path
from .views import Register, Login, Logout, Products, AdminProductList, ChangeProduct, AddProduct, Refunds, RefundAgree, \
    RefundReject, ProductPurchase, PurchaseList, CreateRefund

app_name = 'main'
urlpatterns = [
    path('', Products.as_view(), name="index"),
    path('register/', Register.as_view(), name="register"),
    path('login/', Login.as_view(), name="login"),
    path('logout/', Logout.as_view(), name="logout"),
    path('product-list/', AdminProductList.as_view(), name="product_list"),
    path('change-product/<int:pk>/', ChangeProduct.as_view(), name="change_product"),
    path('add-product/', AddProduct.as_view(), name="add_product"),
    path('refunds/', Refunds.as_view(), name="refunds"),
    path('refund_agree/<int:pk>/', RefundAgree.as_view(), name='refund_agree'),
    path('refund_reject/<int:pk>/', RefundReject.as_view(), name='refund_reject'),
    path('purchase/<int:pk>/', ProductPurchase.as_view(), name='purchase_product'),
    path('purchase-list/', PurchaseList.as_view(), name='purchase_list'),
    path('create-refund/<int:purchase_id>/', CreateRefund.as_view(), name='create_refund'),

]
#completed