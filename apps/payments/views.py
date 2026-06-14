import stripe
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Payment, VendorPayout
from apps.orders.models import Order

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def payment_checkout(request, order_id):
    order = get_object_or_404(Order, pk=order_id, buyer=request.user, status='pending')
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', 'stripe')
        if payment_method == 'cod':
            Payment.objects.create(
                order=order,
                method='cod',
                status='pending',
                amount=order.total,
            )
            order.status = 'confirmed'
            order.save()
            _create_vendor_payouts(order)
            return redirect('payments:success', order_id=order.id)
        elif payment_method == 'stripe':
            intent = stripe.PaymentIntent.create(
                amount=int(order.total * 100),
                currency='php',
                metadata={'order_id': order.id},
            )
            Payment.objects.update_or_create(
                order=order,
                defaults={
                    'method': 'stripe',
                    'status': 'pending',
                    'amount': order.total,
                    'stripe_payment_intent_id': intent.id,
                }
            )
            return JsonResponse({'client_secret': intent.client_secret})
    context = {
        'order': order,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    }
    return render(request, 'payments/checkout.html', context)


@login_required
def payment_success(request, order_id):
    order = get_object_or_404(Order, pk=order_id, buyer=request.user)
    return render(request, 'payments/success.html', {'order': order})


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)
    if event['type'] == 'payment_intent.succeeded':
        intent = event['data']['object']
        order_id = intent['metadata'].get('order_id')
        if order_id:
            try:
                order = Order.objects.get(pk=order_id)
                payment = Payment.objects.get(order=order)
                payment.status = 'success'
                payment.stripe_charge_id = intent.get('latest_charge', '')
                payment.save()
                order.status = 'confirmed'
                order.save()
                _create_vendor_payouts(order)
            except (Order.DoesNotExist, Payment.DoesNotExist):
                pass
    return HttpResponse(status=200)


def _create_vendor_payouts(order):
    for sub_order in order.sub_orders.all():
        VendorPayout.objects.get_or_create(
            sub_order=sub_order,
            defaults={
                'store': sub_order.store,
                'amount': sub_order.vendor_earning,
                'commission_deducted': sub_order.commission,
                'status': 'pending',
            }
        )