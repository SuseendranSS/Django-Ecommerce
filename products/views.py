from django.shortcuts import render , redirect
from django.http import *
from products.models import *
from accounts.models import *
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from accounts.models import CartItems
from django.contrib import messages
from django.urls import reverse
from django.forms.models import model_to_dict

# Create your views here.

def product_details(request , slug):
    try:
        product_obj = product.objects.get(slug = slug)
        context={'product': product_obj}
        if request.GET.get('size'):
            size = request.GET.get('size')
            price = product_obj.get_product_price_by_size(size)
            context['selected_size'] = size
            context['updated_price'] = price
            print(price)
        return render(request, 'products/product.html', context=context)
    except Exception as e:
        print(e)

def update_cart(request):
    if request.method == 'POST' and request.is_ajax():
        product_slug = request.POST.get('product_slug')  # Retrieve the product slug
        quantity = int(request.POST.get('quantity'))

        # Retrieve the CartItems object using the product slug
        cart_item = get_object_or_404(CartItems, product__slug=product_slug)

        # Update the quantity
        cart_item.quantity = quantity
        cart_item.save()

        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request'})

def print_quantity_to_console(request):
    if request.method == 'POST' and request.is_ajax():
        quantity = request.POST.get('quantity')
        print(f"Quantity: {quantity}")  # Print the quantity to the console
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request'})
    
def category_view(request, slug):
    if slug == "all":
        products = product.objects.all() 
        categories = category.objects.all()
        context = {'products': products, 'categories': categories}
        return render(request, 'products/category.html', context)
    elif category.objects.filter(slug=slug).exists():
        products = product.objects.filter(category__slug=slug)
        categories = category.objects.all()
        context = {'products': products, 'categories': categories}
        context['get_products_url'] = reverse('get_products', args=[slug])
        return render(request, 'products/category.html', context)
    else:
        messages.warning(request, "No such category found")
        return redirect('home/index.html')
    
def get_products(request, slug):
    try:
        if slug == "all":
            products = list(product.objects.values())
        else:
            products = list(product.objects.filter(category__slug=slug).prefetch_related('product_images').values())
        
        # Convert each product queryset to dictionary
        for prod in products:
            prod['product_images'] = [img.image.url for img in productImage.objects.filter(product_id=prod['uid'])]
        
        return JsonResponse({'products': products})
    except Exception as e:
        print(e)
        return JsonResponse({'error': 'An error occurred'}, status=500)
