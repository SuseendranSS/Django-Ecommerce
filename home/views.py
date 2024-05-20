from django.shortcuts import render
from products.models import product, category

# Create your views here.
def index_view(request):
    context = {'products': product.objects.all(),'categories': category.objects.all()}
    return render(request , 'home/index.html', context)