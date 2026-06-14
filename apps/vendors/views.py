from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from .models import Store, VendorApplication
from apps.products.models import Product
from apps.orders.models import SubOrder


def store_detail(request, slug):
    store = get_object_or_404(Store, slug=slug, status='approved')
    products = Product.objects.filter(store=store, status='active').prefetch_related('images')
    reviews = store.store_reviews.select_related('reviewer').order_by('-created_at')[:10]
    context = {
        'store': store,
        'products': products,
        'reviews': reviews,
        'policy': getattr(store, 'policy', None),
    }
    return render(request, 'vendors/store_detail.html', context)


@login_required
def apply_vendor(request):
    if hasattr(request.user, 'store'):
        return redirect('vendors:dashboard')
    if hasattr(request.user, 'vendor_application'):
        return render(request, 'vendors/application_status.html', {
            'application': request.user.vendor_application
        })
    if request.method == 'POST':
        VendorApplication.objects.create(
            user=request.user,
            store_name=request.POST.get('store_name'),
            business_type=request.POST.get('business_type'),
            description=request.POST.get('description'),
            is_student=request.POST.get('is_student') == 'on',
            school=request.POST.get('school', ''),
            id_document=request.FILES.get('id_document'),
        )
        messages.success(request, 'Your application has been submitted!')
        return redirect('vendors:application_status')
    return render(request, 'vendors/apply.html')


@login_required
def dashboard(request):
    if not request.user.is_vendor or not hasattr(request.user, 'store'):
        return redirect('vendors:apply')
    store = request.user.store
    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)
    recent_orders = SubOrder.objects.filter(
        store=store, order__created_at__gte=thirty_days_ago
    )
    total_revenue = recent_orders.aggregate(t=Sum('subtotal'))['t'] or 0
    total_orders = recent_orders.count()
    pending_orders = SubOrder.objects.filter(store=store, status='pending').count()
    orders = SubOrder.objects.filter(store=store).select_related('order__buyer').order_by('-order__created_at')[:10]
    low_stock = Product.objects.filter(store=store, track_inventory=True, stock__lte=5, status='active')
    context = {
        'store': store,
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'recent_orders': orders,
        'low_stock': low_stock,
        'product_count': store.products.filter(status='active').count(),
    }
    return render(request, 'vendors/dashboard.html', context)


@login_required
def product_management(request):
    store = get_object_or_404(Store, owner=request.user)
    products = Product.objects.filter(store=store).prefetch_related('images').order_by('-created_at')
    return render(request, 'vendors/products.html', {'store': store, 'products': products})


@login_required
def order_management(request):
    store = get_object_or_404(Store, owner=request.user)
    sub_orders = SubOrder.objects.filter(store=store).select_related(
        'order__buyer'
    ).prefetch_related('items').order_by('-order__created_at')
    status_filter = request.GET.get('status')
    if status_filter:
        sub_orders = sub_orders.filter(status=status_filter)
    return render(request, 'vendors/orders.html', {
        'store': store, 'sub_orders': sub_orders, 'status_filter': status_filter
    })


@login_required
def earnings(request):
    store = get_object_or_404(Store, owner=request.user)
    payouts = store.payouts.order_by('-paid_at')
    pending_earnings = store.payouts.filter(status='pending').aggregate(t=Sum('amount'))['t'] or 0
    total_earned = store.payouts.filter(status='paid').aggregate(t=Sum('amount'))['t'] or 0
    return render(request, 'vendors/earnings.html', {
        'store': store,
        'payouts': payouts,
        'pending_earnings': pending_earnings,
        'total_earned': total_earned,
    })