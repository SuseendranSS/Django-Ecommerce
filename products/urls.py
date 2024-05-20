from django.urls import path
from products.views import *

urlpatterns = [
    path('print_quantity_to_console/', print_quantity_to_console, name='print_quantity_to_console'),
    path('<slug>/', product_details, name="product_details"),
    path('update_cart/', update_cart, name='update_cart'),
    path('category/<str:slug>', category_view,name = 'category_view' ),
    path('get_products/<str:slug>', get_products, name='get_products'),
    
]
