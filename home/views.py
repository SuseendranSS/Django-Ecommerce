from django.shortcuts import render
from products.models import product, category

# Create your views here.
def index_view(request):
    try:
        context = {'products': product.objects.all(),'categories': category.objects.all()}
        return render(request , 'home/index.html', context)
    except Exception as e:
        print(e)