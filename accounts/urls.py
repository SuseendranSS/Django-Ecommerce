from django.urls import path
from accounts import views as v1
from products import views as v2

urlpatterns = [
    path('login/', v1.login_view, name="login_view"),
    path('logout/', v1.logout_view, name='logout_view'),
    path('signup/', v1.signup_view),
    path('activate/<email_token>/', v1.activate_view),
    path('cart/', v1.cart, name="cart"),
    path('add_to_cart/<uid>/', v1.add_to_cart, name="add_to_cart"),
    path('apply_coupon/', v1.apply_coupon, name='apply_coupon'),
    path('remove_from_cart/<cart_item_uid>/', v1.remove_from_cart, name="remove_from_cart"),
    path('remove_coupon/<str:coupon_code>/', v1.remove_coupon, name='remove_coupon'),
    path('payment/', v1.payment_view, name='payment_view'),
    path('success/', v1.success_view, name='success_view'),
]
