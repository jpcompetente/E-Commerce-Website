from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Product, Category, Wishlist


def home(request):
    featured_products = Product.objects.filter(
        status='active', is_featured=True
    ).select_related('store', 'category').prefetch_related('images')[:8]
    new_arrivals = Product.objects.filter(
        status='active'
    ).select_related('store').prefetch_related('images').order_by('-created_at')[:8]
    best_sellers = Product.objects.filter(
        status='active'
    ).select_related('store').prefetch_related('images').order_by('-sales_count')[:8]
    top_categories = Category.objects.filter(
        level=0, is_active=True
    ).order_by('order')[:8]
    context = {
        'featured_products': featured_products,
        'new_arrivals': new_arrivals,
        'best_sellers': best_sellers,
        'top_categories': top_categories,
    }
    return render(request, 'home.html', context)


def product_list(request):
    products = Product.objects.filter(status='active').select_related('store', 'category').prefetch_related('images')
    q = request.GET.get('q', '')
    if q:
        products = products.filter(
            Q(name__icontains=q) | Q(description__icontains=q) | Q(tags__name__icontains=q)
        ).distinct()
    category_slug = request.GET.get('category')
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category__in=category.get_descendants(include_self=True))
    else:
        category = None
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    sort = request.GET.get('sort', '-created_at')
    sort_map = {
        'newest': '-created_at',
        'oldest': 'created_at',
        'price_asc': 'price',
        'price_desc': '-price',
        'popular': '-sales_count',
        'rating': '-rating',
    }
    products = products.order_by(sort_map.get(sort, '-created_at'))
    paginator = Paginator(products, 24)
    page = paginator.get_page(request.GET.get('page'))
    categories = Category.objects.filter(level=0, is_active=True)
    context = {
        'products': page,
        'categories': categories,
        'current_category': category,
        'search_query': q,
        'current_sort': sort,
    }
    return render(request, 'products/list.html', context)


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related('store', 'category').prefetch_related('images', 'variants', 'reviews'),
        slug=slug, status='active'
    )
    Product.objects.filter(pk=product.pk).update(views=product.views + 1)
    related = Product.objects.filter(
        category=product.category, status='active'
    ).exclude(pk=product.pk).prefetch_related('images')[:4]
    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()
    context = {
        'product': product,
        'related_products': related,
        'in_wishlist': in_wishlist,
        'reviews': product.reviews.filter(is_approved=True).select_related('reviewer')[:10],
    }
    return render(request, 'products/detail.html', context)


@login_required
@require_POST
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    obj, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if not created:
        obj.delete()
        return JsonResponse({'status': 'removed'})
    return JsonResponse({'status': 'added'})


@login_required
def wishlist(request):
    items = Wishlist.objects.filter(user=request.user).select_related(
        'product__store'
    ).prefetch_related('product__images')
    return render(request, 'products/wishlist.html', {'items': items})