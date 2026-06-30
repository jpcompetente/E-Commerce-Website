from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Avg, Count
from .models import Review, ReviewReply
from apps.orders.models import OrderItem


def _recalculate_product_rating(product):
    agg = product.reviews.filter(is_approved=True).aggregate(avg=Avg('rating'), cnt=Count('id'))
    product.rating = agg['avg'] or 0
    product.review_count = agg['cnt'] or 0
    product.save(update_fields=['rating', 'review_count'])


@login_required
@require_POST
def add_review(request, product_id):
    from apps.products.models import Product
    product = get_object_or_404(Product, pk=product_id)

    if Review.objects.filter(product=product, reviewer=request.user).exists():
        messages.warning(request, 'You already reviewed this product.')
        return redirect(product.get_absolute_url())

    order_item = OrderItem.objects.filter(
        product=product,
        sub_order__order__buyer=request.user,
        sub_order__status='delivered'
    ).first()
    if not order_item:
        messages.error(request, 'You can only review products you have purchased and received.')
        return redirect(product.get_absolute_url())

    try:
        rating = int(request.POST.get('rating', 0))
        if not (1 <= rating <= 5):
            raise ValueError
    except (TypeError, ValueError):
        messages.error(request, 'Please select a rating from 1 to 5 stars.')
        return redirect(product.get_absolute_url())

    body = request.POST.get('body', '').strip()
    if not body:
        messages.error(request, 'Please write your review.')
        return redirect(product.get_absolute_url())

    Review.objects.create(
        product=product,
        order_item=order_item,
        reviewer=request.user,
        rating=rating,
        body=body,
        is_verified_purchase=True,
    )
    _recalculate_product_rating(product)
    messages.success(request, 'Thank you for your review!')
    return redirect(product.get_absolute_url())


@login_required
@require_POST
def delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk, reviewer=request.user)
    product = review.product
    review.delete()
    _recalculate_product_rating(product)
    messages.success(request, 'Your review has been deleted.')
    return redirect(product.get_absolute_url())


@login_required
@require_POST
def reply_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if not request.user.is_vendor or not hasattr(request.user, 'store') or review.product.store_id != request.user.store.id:
        return redirect('vendors:dashboard')

    body = request.POST.get('body', '').strip()
    if not body:
        messages.error(request, 'Reply cannot be empty.')
        return redirect('vendors:store_reviews')

    ReviewReply.objects.update_or_create(
        review=review,
        defaults={'author': request.user, 'body': body}
    )
    messages.success(request, 'Reply posted.')
    return redirect('vendors:store_reviews')
