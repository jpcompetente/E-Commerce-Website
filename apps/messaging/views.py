from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Q
from .models import Conversation, Message
from apps.vendors.models import Store
from apps.products.models import Product


@login_required
def inbox(request):
    conversations = Conversation.objects.filter(
        Q(buyer=request.user) | Q(store__owner=request.user)
    ).select_related('buyer', 'store', 'product').prefetch_related('messages')
    return render(request, 'messaging/inbox.html', {'conversations': conversations})


@login_required
def conversation_detail(request, pk):
    conversation = get_object_or_404(Conversation, pk=pk)
    if request.user != conversation.buyer and request.user != conversation.store.owner:
        return redirect('messaging:inbox')
    conversation.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
    return render(request, 'messaging/conversation.html', {'conversation': conversation})


@login_required
@require_POST
def send_message(request, pk):
    conversation = get_object_or_404(Conversation, pk=pk)
    if request.user != conversation.buyer and request.user != conversation.store.owner:
        return redirect('messaging:inbox')
    body = request.POST.get('body', '').strip()
    if body:
        Message.objects.create(
            conversation=conversation,
            sender=request.user,
            body=body,
        )
        conversation.save()
        from apps.notifications.utils import notify
        recipient = conversation.store.owner if request.user == conversation.buyer else conversation.buyer
        sender_name = request.user.get_full_name() or request.user.email
        notify(
            recipient=recipient,
            title=f'New message from {sender_name}',
            message=body[:100],
            link=f'/messages/conversation/{conversation.pk}/',
            notif_type='message',
        )
    return redirect('messaging:conversation', pk=pk)


@login_required
@require_POST
def delete_conversation(request, pk):
    conversation = get_object_or_404(Conversation, pk=pk)
    if request.user != conversation.buyer and request.user != conversation.store.owner:
        return redirect('messaging:inbox')
    conversation.delete()
    messages.success(request, 'Conversation deleted.')
    return redirect('messaging:inbox')


@login_required
def start_conversation(request, store_slug):
    store = get_object_or_404(Store, slug=store_slug)
    if request.user == store.owner:
        return redirect('messaging:inbox')
    product_id = request.GET.get('product')
    product = None
    if product_id:
        product = Product.objects.filter(pk=product_id).first()
    conversation, created = Conversation.objects.get_or_create(
        buyer=request.user,
        store=store,
        product=product,
        defaults={'subject': f"Inquiry about {product.name}" if product else f"Inquiry to {store.name}"}
    )
    if created and request.method == 'POST':
        body = request.POST.get('body', '').strip()
        if body:
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                body=body,
            )
    elif request.method == 'POST':
        body = request.POST.get('body', '').strip()
        if body:
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                body=body,
            )
    return redirect('messaging:conversation', pk=conversation.pk)
