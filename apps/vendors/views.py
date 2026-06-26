from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from .models import Store, VendorApplication
from apps.products.models import Product
from apps.orders.models import Order, SubOrder
from apps.users.models import User


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
    if not request.user.is_vendor:
        return redirect('vendors:apply')
    store = get_object_or_404(Store, owner=request.user)
    products = Product.objects.filter(store=store).prefetch_related('images').order_by('-created_at')
    return render(request, 'vendors/products.html', {'store': store, 'products': products})


@login_required
def order_management(request):
    if not request.user.is_vendor:
        return redirect('vendors:apply')
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
    if not request.user.is_vendor:
        return redirect('vendors:apply')
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


# ─── SUPERADMIN VIEWS ─────────────────────────────────────────────────────────

@staff_member_required
def superadmin_dashboard(request):
    total_users = User.objects.count()
    total_vendors = User.objects.filter(role='vendor').count()
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    pending_applications = VendorApplication.objects.filter(status='pending').count()
    recent_orders = Order.objects.select_related('buyer').order_by('-created_at')[:5]
    recent_users = User.objects.order_by('-date_joined')[:5]
    context = {
        'total_users': total_users,
        'total_vendors': total_vendors,
        'total_products': total_products,
        'total_orders': total_orders,
        'pending_applications': pending_applications,
        'recent_orders': recent_orders,
        'recent_users': recent_users,
    }
    return render(request, 'superadmin/dashboard.html', context)


@staff_member_required
def superadmin_users(request):
    users = User.objects.order_by('-date_joined')
    role_filter = request.GET.get('role', '')
    if role_filter:
        users = users.filter(role=role_filter)
    return render(request, 'superadmin/users.html', {'users': users, 'role_filter': role_filter})


@staff_member_required
def superadmin_toggle_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.is_active = not user.is_active
    user.save()
    status = 'activated' if user.is_active else 'deactivated'
    messages.success(request, f'{user.email} has been {status}.')
    return redirect('vendors:superadmin_users')


@staff_member_required
def superadmin_applications(request):
    status_filter = request.GET.get('status', 'pending')
    applications = VendorApplication.objects.select_related('user').filter(
        status=status_filter
    ).order_by('-created_at')
    return render(request, 'superadmin/applications.html', {
        'applications': applications,
        'status_filter': status_filter,
    })


@staff_member_required
def superadmin_approve_vendor(request, pk):
    application = get_object_or_404(VendorApplication, pk=pk)
    application.status = 'approved'
    application.save()
    application.user.role = 'vendor'
    application.user.save()
    Store.objects.get_or_create(
        owner=application.user,
        defaults={
            'name': application.store_name,
            'description': application.description,
            'is_student': application.is_student,
            'school': application.school,
            'status': 'approved',
        }
    )
    messages.success(request, f'{application.store_name} approved!')
    return redirect('vendors:superadmin_applications')


@staff_member_required
def superadmin_reject_vendor(request, pk):
    application = get_object_or_404(VendorApplication, pk=pk)
    application.status = 'rejected'
    application.save()
    messages.warning(request, f'{application.store_name} rejected.')
    return redirect('vendors:superadmin_applications')


@staff_member_required
def superadmin_products(request):
    products = Product.objects.select_related('store', 'category').prefetch_related('images').order_by('-created_at')
    return render(request, 'superadmin/products.html', {'products': products})


@staff_member_required
def superadmin_orders(request):
    orders = Order.objects.select_related('buyer').order_by('-created_at')
    status_filter = request.GET.get('status', '')
    if status_filter:
        orders = orders.filter(status=status_filter)
    return render(request, 'superadmin/orders.html', {'orders': orders, 'status_filter': status_filter})


from apps.products.models import ProductImage, Category
from django import forms

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'product_type', 'status',
                  'price', 'compare_at_price', 'stock', 'track_inventory', 'sku', 'weight', 'tags']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

@login_required
def add_product(request):
    if not request.user.is_vendor:
        return redirect('vendors:apply')
    store = get_object_or_404(Store, owner=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST)
        images = request.FILES.getlist('images')
        if form.is_valid():
            product = form.save(commit=False)
            product.store = store
            product.save()
            form.save_m2m()
            for i, image in enumerate(images):
                ProductImage.objects.create(
                    product=product,
                    image=image,
                    is_primary=(i == 0)
                )
            messages.success(request, f'{product.name} added successfully!')
            return redirect('vendors:products')
    else:
        form = ProductForm()
    return render(request, 'vendors/product_form.html', {'form': form, 'store': store, 'action': 'Add'})

@login_required
def edit_product(request, pk):
    if not request.user.is_vendor:
        return redirect('vendors:apply')
    store = get_object_or_404(Store, owner=request.user)
    product = get_object_or_404(Product, pk=pk, store=store)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        images = request.FILES.getlist('images')
        if form.is_valid():
            form.save()
            for i, image in enumerate(images):
                ProductImage.objects.create(
                    product=product,
                    image=image,
                    is_primary=(i == 0 and not product.images.exists())
                )
            messages.success(request, f'{product.name} updated!')
            return redirect('vendors:products')
    else:
        form = ProductForm(instance=product)
    return render(request, 'vendors/product_form.html', {'form': form, 'store': store, 'product': product, 'action': 'Edit'})

@login_required
def delete_product(request, pk):
    if not request.user.is_vendor:
        return redirect('vendors:apply')
    store = get_object_or_404(Store, owner=request.user)
    product = get_object_or_404(Product, pk=pk, store=store)
    product.delete()
    messages.success(request, 'Product deleted.')
    return redirect('vendors:products')








@login_required
def update_order_status(request, pk):
    if not request.user.is_vendor:
        return redirect('vendors:apply')
    store = get_object_or_404(Store, owner=request.user)
    sub_order = get_object_or_404(SubOrder, pk=pk, store=store)
    new_status = request.POST.get('status')
    valid_statuses = ['confirmed', 'shipped', 'delivered', 'cancelled']
    if new_status in valid_statuses:
        sub_order.status = new_status
        sub_order.save()
        # Sync main order status
        order = sub_order.order
        all_sub_orders = order.sub_orders.all()
        statuses = [s.status for s in all_sub_orders]
        if all(s == 'delivered' for s in statuses):
            order.status = 'delivered'
        elif all(s == 'cancelled' for s in statuses):
            order.status = 'cancelled'
        elif any(s == 'shipped' for s in statuses):
            order.status = 'shipped'
        elif any(s == 'confirmed' for s in statuses):
            order.status = 'confirmed'
        order.save()
        messages.success(request, f'Order #{order.order_number} updated to {new_status}!')
    return redirect('vendors:orders')

