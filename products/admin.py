from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(category)

class productImageAdmin(admin.StackedInline):
    model = productImage

class productAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'category', 'price']
    inlines = [productImageAdmin]

@admin.register(ColorVariant)
class ColorVariantAdmin(admin.ModelAdmin):
    list_display = ['color_name', 'price']
    model = ColorVariant

@admin.register(SizeVariant)
class SizeVariantAdmin(admin.ModelAdmin):
    list_display = ['size_name', 'price']
    model = SizeVariant

admin.site.register(product, productAdmin)
admin.site.register(productImage)
admin.site.register(Coupon)