from django.shortcuts import render
from django.db.models import Prefetch
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, logout
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .models import Message

User = get_user_model()

@login_required
@require_POST
def delete_user(request):
    """
    View to allow users to delete their own account.
    """
    user = request.user
    logout(request)  # Log user out first
    user.delete()    # Triggers post_delete signal
    return redirect('home')  # or any success URL


@login_required
def send_message(request, receiver_id, parent_id=None):
    receiver = get_object_or_404(User, id=receiver_id)
    parent_message = None

    if parent_id:
        parent_message = get_object_or_404(Message, id=parent_id)

    if request.method == "POST":
        content = request.POST.get("content")
        if content:
            Message.objects.create(
                sender=request.user,
                receiver=receiver,
                content=content,
                parent_message=parent_message
            )
            return redirect("inbox")  # or a thread view

    return render(request, "messaging/send_message.html", {
        "receiver": receiver,
        "parent_message": parent_message
    })


@login_required
def inbox(request):
    messages = Message.objects.filter(receiver=request.user, parent_message__isnull=True) \
        .select_related('sender', 'receiver') \
        .prefetch_related(
            Prefetch('replies', queryset=Message.objects.select_related('sender', 'receiver'))
        )

    return render(request, "messaging/inbox.html", {
        "messages": messages
    })


@login_required
def unread_messages(request):
    # This uses the custom manager and retrieves only needed fields
    unread_msgs = Message.unread.for_user(request.user).only('id', 'sender', 'content', 'timestamp')

    return render(request, 'messaging/unread_inbox.html', {
        'unread_messages': unread_msgs
    })
