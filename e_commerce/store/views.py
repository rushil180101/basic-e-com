from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
import json
import datetime
from .models import *
from .forms import CreateUserForm


def store(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'store/store.html', context)


def cart(request):
    if request.user.is_authenticated:
        customer = Customer.objects.get(user=request.user)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        order_items = OrderItem.objects.filter(order=order)
        total_items = sum([order_item.quantity for order_item in order_items])
        total_amount = sum([order_item.get_total for order_item in order_items])
        shipping = False
        for order_item in order_items:
            if not order_item.product.digital:
                shipping = True
    else:
        order_items = []
        total_items = 0
        total_amount = 0
        shipping = False

    context = {
        'order_items': order_items,
        'total_items': total_items,
        'total_amount': total_amount,
        'shipping': shipping
    }
    return render(request, 'store/cart.html', context)


def checkout(request):
    if request.user.is_authenticated:
        customer = Customer.objects.get(user=request.user)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        order_items = OrderItem.objects.filter(order=order)
        total_items = sum([order_item.quantity for order_item in order_items])
        total_amount = sum([order_item.get_total for order_item in order_items])
        shipping = False
        for order_item in order_items:
            if not order_item.product.digital:
                shipping = True
    else:
        order_items = []
        total_items = 0
        total_amount = 0
        shipping = False

    context = {
        'order_items': order_items,
        'total_items': total_items,
        'total_amount': total_amount,
        'shipping': shipping
    }
    return render(request, 'store/checkout.html', context)


def update_item(request, pk, update_action, current_page):
    if request.user.is_authenticated:
        customer = Customer.objects.get(user=request.user)
        product = Product.objects.get(pk=pk)
        order = Order.objects.get_or_create(customer=customer, complete=False)
        order_item = OrderItem.objects.get_or_create(order=order[0], product=product)[0]
        if update_action == 1:
            order_item.quantity += 1
            order_item.save()
        elif update_action == 0:
            order_item.quantity -= 1
            if order_item.quantity <= 0:
                order_item.delete()
            else:
                order_item.save()

        if current_page == 1:
            return redirect('store')
        elif current_page == 2:
            return redirect('cart')
    else:
        messages.info(request, 'You need to login to add items to cart ...')
        return redirect('store')


def view_product(request, pk):
    product = Product.objects.get(pk=pk)
    context = {'product': product}
    return render(request, 'store/view_product.html', context)


def process_order(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    if request.user.is_authenticated:
        customer = Customer.objects.get(user=request.user)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        order_items = OrderItem.objects.filter(order=order)
        total_amount_backend = sum([order_item.get_total for order_item in order_items])
        total_amount_frontend = float(data['user_info']['total_amount'])
        order.transaction_id = transaction_id

        if total_amount_frontend == total_amount_backend:
            order.complete = True

            order.save()

            if order.shipping:
                ShippingAddress.objects.create(
                    customer=customer,
                    order=order,
                    address=data['shipping_info']['address'],
                    city=data['shipping_info']['city'],
                    state=data['shipping_info']['state'],
                    zipcode=data['shipping_info']['zipcode'],
                )
        else:
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect('store')

    else:
        print('User not logged in')

    return JsonResponse('Payment completed', safe=False)


def register_page(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        print(form)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            first_name = user.first_name
            last_name = user.last_name
            email = user.email
            name = str(first_name) + ' ' + str(last_name)
            customer, created = Customer.objects.get_or_create(user=user, name=name, email=email)
            customer.save()
            messages.success(request, 'Account created successfully for ' + username)
            return redirect('login')

    context = {'form': form}
    return render(request, 'store/register.html', context)


def login_page(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('store')
        else:
            messages.info(request, 'Username of Password incorrect')

    context = {}
    return render(request, 'store/login.html', context)


def logout_user(request):
    logout(request)
    return redirect('store')

