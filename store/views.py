from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import viewsets
from .models import Category, Order, OrderItem, Product
from .serializers import CategorySerializer, OrderSerializer, ProductSerializer
from django.db.models import Sum
from django.utils import timezone


def dashboard_view(request):
  today = timezone.now().date()

  orders = Order.objects.all().order_by('-created_at')
  # total_amount o'rniga total_price ishlatamiz
  total_revenue = (
      orders.aggregate(Sum('total_price'))['total_price__sum'] or 0
  )
  today_revenue = (
      orders.filter(created_at__date=today)
      .aggregate(Sum('total_price'))['total_price__sum']
      or 0
  )
  total_orders_count = orders.count()

  context = {
      'orders': orders[:10],
      'total_revenue': total_revenue,
      'today_revenue': today_revenue,
      'total_orders_count': total_orders_count,
  }
  return render(request, 'dashboard.html', context)
# DRF ViewSets
class CategoryViewSet(viewsets.ModelViewSet):
  queryset = Category.objects.all()
  serializer_class = CategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
  queryset = Product.objects.all()
  serializer_class = ProductSerializer
  search_fields = ('name', 'sku')


class OrderViewSet(viewsets.ModelViewSet):
  queryset = Order.objects.all().order_by('-created_at')
  serializer_class = OrderSerializer


# POS va savat funksiyalari
def index(request):
  products = Product.objects.all()
  return render(request, 'index.html', {'products': products})


def add_selected_to_cart(request):
  if request.method == 'POST':
    product_ids = request.POST.getlist('product_ids')
    quantities = request.POST.getlist('quantities')

    cart = request.session.get('cart', {})

    for prod_id, qty in zip(product_ids, quantities):
      if qty and int(qty) > 0:
        cart[prod_id] = cart.get(prod_id, 0) + int(qty)

    request.session['cart'] = cart
    return redirect('cart_detail')
  return redirect('index')


def cart_detail(request):
  cart = request.session.get('cart', {})
  cart_items = []
  total_price = 0

  for prod_id, quantity in cart.items():
    product = get_object_or_404(Product, id=prod_id)
    subtotal = product.price * quantity
    total_price += subtotal
    cart_items.append(
        {'product': product, 'quantity': quantity, 'subtotal': subtotal}
    )

  context = {'cart_items': cart_items, 'total_price': total_price}
  return render(request, 'cart.html', context)


def create_order(request):
  cart = request.session.get('cart', {})
  if not cart:
    return redirect('cart_detail')

  order = Order.objects.create()

  for prod_id, quantity in cart.items():
    product = get_object_or_404(Product, id=prod_id)
    OrderItem.objects.create(
        order=order, product=product, quantity=quantity, price=product.price
    )
    product.stock -= quantity
    product.save()

  request.session['cart'] = {}
  return redirect('receipt', order_id=order.id)


def receipt_view(request, order_id):
  order = get_object_or_404(Order, id=order_id)
  return render(request, 'receipt.html', {'order': order})