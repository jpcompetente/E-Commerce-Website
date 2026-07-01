from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import Cart, CartItem, Order, SubOrder, OrderItem
from apps.products.models import Product, ProductVariant


def cart_detail(request):
    cart = _get_cart(request)
    cart_items = cart.items.select_related('product', 'variant').prefetch_related('product__images', 'product__store') if cart else []
    cart_total = cart.total if cart else 0
    return render(request, 'orders/cart.html', {
        'cart': cart,
        'cart_items': cart_items,
        'cart_total': cart_total,
    })


@login_required
@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id, status='active')
    cart = _get_cart(request)
    variant_id = request.POST.get('variant_id')
    variant = get_object_or_404(ProductVariant, pk=variant_id) if variant_id else None
    item, created = CartItem.objects.get_or_create(
        cart=cart, product=product, variant=variant,
        defaults={'quantity': 1}
    )
    if not created:
        item.quantity += 1
        item.save()
    messages.success(request, f'{product.name} added to cart!')
    return redirect('orders:cart')


@require_POST
def update_cart(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id)
    quantity = int(request.POST.get('quantity', 1))
    if quantity > 0:
        item.quantity = quantity
        item.save()
    else:
        item.delete()
    return redirect('orders:cart')


@require_POST
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id)
    item.delete()
    return redirect('orders:cart')


@login_required
def checkout(request):
    cart = _get_cart(request)
    if not cart or cart.items.count() == 0:
        return redirect('orders:cart')
    addresses = request.user.addresses.all()
    return render(request, 'orders/checkout.html', {'cart': cart, 'addresses': addresses})


@login_required
@require_POST
def place_order(request):
    cart = _get_cart(request)
    if not cart or cart.items.count() == 0:
        return redirect('orders:cart')
    address_id = request.POST.get('address_id')
    address = get_object_or_404(request.user.addresses, pk=address_id)
    shipping_address = {
        'full_name': address.full_name,
        'phone': address.phone,
        'street': address.street,
        'city': address.city,
        'province': address.province,
        'postal_code': address.postal_code,
        'country': address.country,
    }
    order = Order.objects.create(
        buyer=request.user,
        shipping_address=shipping_address,
        total=cart.total,
    )
    stores = {}
    for item in cart.items.all():
        store = item.product.store
        if store.id not in stores:
            stores[store.id] = {'store': store, 'items': []}
        stores[store.id]['items'].append(item)
    for store_data in stores.values():
        subtotal = sum(i.subtotal for i in store_data['items'])
        from django.conf import settings
        commission = subtotal * settings.MARKETPLACE_COMMISSION_RATE
        sub_order = SubOrder.objects.create(
            order=order,
            store=store_data['store'],
            subtotal=subtotal,
            commission=commission,
            vendor_earning=subtotal - commission,
        )
        for item in store_data['items']:
            OrderItem.objects.create(
                sub_order=sub_order,
                product=item.product,
                variant=item.variant,
                quantity=item.quantity,
                price=item.variant.effective_price if item.variant else item.product.price,
            )
    cart.items.all().delete()
    return redirect('payments:checkout', order_id=order.id)


@login_required
def order_list(request):
    orders = Order.objects.filter(buyer=request.user).order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_detail(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, buyer=request.user)
    from apps.reviews.models import Review
    reviewed_product_ids = set(
        Review.objects.filter(reviewer=request.user).values_list('product_id', flat=True)
    )
    return render(request, 'orders/order_detail.html', {
        'order': order,
        'reviewed_product_ids': reviewed_product_ids,
    })


@login_required
@require_POST
def cancel_order(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, buyer=request.user)
    if order.status == 'pending':
        order.status = 'cancelled'
        order.save()
        order.sub_orders.update(status='cancelled')
        messages.success(request, 'Order cancelled successfully.')
    else:
        messages.error(request, 'Only pending orders can be cancelled.')
    return redirect('orders:order_detail', order_number=order_number)


def _get_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key, user=None)
    return cart

