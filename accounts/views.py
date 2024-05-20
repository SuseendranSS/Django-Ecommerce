from django.shortcuts import render , redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate , login , logout
from django.http import HttpResponseRedirect , HttpResponse , JsonResponse
from .models import Profile
from products.models import *
from accounts.models import Cart, CartItems
from django.utils.crypto import get_random_string
from django.contrib.auth.decorators import login_required
from django.conf import settings


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user_obj = User.objects.filter(email=email)

        if not user_obj.exists():
            messages.warning(request, 'Account not found')
            return render(request, 'accounts/login.html')

        if not user_obj[0].profile.is_email_verified:
            messages.warning(request, 'Your Account is not verified.')
            return render(request, 'accounts/login.html')

        user_obj = authenticate(username = email , password = password)
        if user_obj:
            login(request , user_obj)
            return redirect('/')
        messages.warning(request, 'Invalid credentials')

    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('home:index_view')

def signup_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        user_obj = User.objects.filter(email=email)

        if user_obj.exists():
            messages.warning(request, 'Email already exists.')
            return HttpResponseRedirect(request.path_info)

        user_obj = User.objects.create(first_name=first_name, last_name=last_name, email=email, username=email)
        user_obj.set_password(password)
        user_obj.save()
        messages.success(request, 'An email has been sent to your mail id.')
        return HttpResponseRedirect(request.path_info)

    return render(request, 'accounts/signup.html')

def activate_view(request, email_token):
    try:
        user = Profile.objects.get(email_token=email_token)
        user.is_email_verified = True
        user.save()
        return redirect('accounts/login.html')#send a confirmation mail here
    except user.DoesNotExist:
        return HttpResponse('Invalid Email Token')

def add_to_cart(request, uid):
    variant = request.GET.get('variant')
    print(variant)
    product_obj = product.objects.get(uid=uid)
    user = request.user
    cart, _ = Cart.objects.get_or_create(user=user, is_paid=False)

    cart_item, created = CartItems.objects.get_or_create(cart=cart, product=product_obj)
    if variant:
        size_variant = SizeVariant.objects.get(size_name=variant)
        cart_item.size_variant = size_variant

    # If the product is already in the cart, increase its quantity by 1
    if not created:
        cart_item.quantity += 1
    cart_item.save()

    return redirect(request.META.get('HTTP_REFERER', '/'))


def apply_coupon(request):
    if request.method == 'POST':
        cart = Cart.objects.filter(user=request.user, is_paid=False).first()
        if not cart:
            messages.error(request, 'Cart not found.')
            return redirect('cart')

        coupon_code = request.POST.get('coupon')
        coupon_obj = Coupon.objects.filter(coupon_code__iexact=coupon_code).first()
        
        if not coupon_obj:
            messages.warning(request, 'Invalid Coupon')
        else:
            # Calculate the total price without considering any applied coupons
            total_price = cart.total_price
            print("Total price before applying coupon from apply_coupon view : ", total_price)
            
            # Check if the coupon is already applied
            applied_coupons = request.session.get('applied_coupons', [])
            if str(coupon_obj.pk) in [coupon['coupon_id'] for coupon in applied_coupons]:
                messages.warning(request, 'Coupon already applied')
            elif total_price < coupon_obj.minimum_amount:
                messages.warning(request, f'Total should be greater than ₹{coupon_obj.minimum_amount} to avail this coupon')
            elif coupon_obj.is_expired:
                messages.warning(request, 'Sorry, this coupon has expired')
            else:
                # Associate coupon with the cart
                cart.coupon = coupon_obj
                cart.save()

                # Calculate discounted total price
                discounted_total_price = total_price - coupon_obj.discount_price
                cart.total_price = discounted_total_price
                cart.save()
                print("Total price after applying coupon from apply_coupon view : ", discounted_total_price)
                print("Total price adding to the cart.total_price : ", cart.total_price)

                # Store coupon information in session
                applied_coupons.append({
                    'coupon_id': str(coupon_obj.pk),  # Convert UUID to string
                    'coupon_code': coupon_obj.coupon_code,
                    'discount_price': coupon_obj.discount_price
                })
                request.session['applied_coupons'] = applied_coupons

                messages.success(request, 'Coupon applied successfully')

                # Pass discounted total price as context
                context = {
                    'cart_items': cart.cart_items.all(),
                    'total_price': discounted_total_price,
                }
                return render(request, 'accounts/cart.html', context)
        
    return redirect('cart')

@login_required
def cart(request):
    cart = Cart.objects.filter(user=request.user, is_paid=False).first()
    if cart:
        cart.coupon = None
        cart.save()

        # Remove coupon information from session data
        request.session.pop('applied_coupons', None)
        
        cart_items = cart.cart_items.all()

        # Calculate total price without considering any applied coupons
        cart.total_price = cart.get_cart_total()
        cart.save()
        print("Total price before applying coupon from cart view : ", cart.total_price)

        # Calculate total price for each cart item
        for cart_item in cart_items:
            cart_item.pdt_total_price = cart_item.get_total_price()
            cart_item.save()

        # Pass the appropriate total price to the context
        context = {
            'cart_items': cart_items,
            'total_price': cart.total_price,
        }
    else:
        cart_items = []
        total_price = 0
        context = {
            'cart_items': cart_items,
            'total_price': total_price,
        }

    return render(request, 'accounts/cart.html', context)


def remove_from_cart(request, cart_item_uid):
    cart_item = CartItems.objects.get(uid = cart_item_uid)

    if cart_item:
        cart_item.delete()
    else:
        messages.error(request, 'Item not found in cart.')

    return redirect('cart')

def remove_coupon(request, coupon_code):
    print("********************")
    print("The clicked coupon : ", coupon_code)
    if request.method == 'GET':
        applied_coupons = request.session.get('applied_coupons', [])
        for i in applied_coupons:
            print("********************")
            print("applied coupons : ", i)

        # Find the clicked coupon in session data
        updated_coupons = []
        for coupon in applied_coupons:
            if coupon['coupon_code'] != coupon_code:
                updated_coupons.append(coupon)

        for i in updated_coupons:
            print("********************")
            print("updated coupons : ", i)
            
        request.session['applied_coupons'] = updated_coupons
        request.session.modified = True  # Mark the session as modified
        
        print("********************")
        print("Session data after modification:", request.session['applied_coupons'])
        
        messages.success(request, 'Coupon removed successfully.')
        return redirect('cart')
    else:
        messages.error(request, "Invalid Request")
        return redirect('cart')

def payment_view(request):
    # Retrieve the cart and its details
    cart = Cart.objects.filter(user=request.user, is_paid=False).first()
    if not cart:
        # Handle case where cart is not found
        messages.error(request, 'Cart not found.')
        return redirect('cart')

    # Get the total price of the cart
    total_price = cart.total_price

    # Print total price for debugging
    print("Total price:", total_price)

    # Create Razorpay order
    razorpay_client = settings.RAZORPAY_CLIENT

    order_amount = int(total_price * 100)  # Razorpay requires the amount in paisa
    order_currency = 'INR'
    order_receipt = 'order_rcptid_' + get_random_string(length=10)
    order_data = {
        'amount': order_amount,
        'currency': order_currency,
        'receipt': order_receipt,
        'payment_capture': 1,
    }

    try:
        razorpay_order = razorpay_client.order.create(data=order_data)
        cart.razorpay_order_id = razorpay_order['id']
        cart.save()
        # Print order data for debugging
        print("Razorpay Order Data:", razorpay_order)
    except Exception as e:
        print("Error:", str(e))
        return JsonResponse({'error': str(e)}, status=500)

    # Return Razorpay order details as JSON response
    return JsonResponse({
        'razorpay_order_id': razorpay_order['id'],
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'order_amount': order_amount,
        'order_currency': order_currency,
        'order_receipt': order_receipt,
    })

@login_required
def success_view(request):
    order_id = request.GET.get('order_id')
    cart = Cart.objects.get(razorpay_order_id=order_id)
    cart.is_paid = True
    cart.save()

    # Fetch necessary details
    user_email = request.user.email
    payment_id = cart.razorpay_order_id
    order_amount = cart.total_price

    # Pass details to template
    context = {
        'user_email': user_email,
        'order_id': order_id,
        'payment_id': payment_id,
        'order_amount': order_amount,
    }

    return render(request, 'accounts/payment.html', context)