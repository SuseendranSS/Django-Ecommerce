
from .models import Profile

def cart_count(request):
    cart_count = 0
    if request.user.is_authenticated:
        profile = Profile.objects.filter(user=request.user).first()
        if profile:
            cart_count = profile.get_cart_count()
    return {'cart_count': cart_count}
