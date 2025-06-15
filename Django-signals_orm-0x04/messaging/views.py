from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, logout
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

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

