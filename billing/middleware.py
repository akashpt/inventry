from django.shortcuts import redirect
from django.urls import reverse

from .models import UserProfile


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        login_url = reverse("login")
        public_paths = [
            login_url,
            reverse("register"),
            reverse("forgot_username"),
            "/admin/",
            "/static/",
            "/media/",
        ]

        is_public = any(request.path.startswith(path) for path in public_paths)
        if request.path == "/users/new" and not UserProfile.objects.exists():
            is_public = True

        if not request.user.is_authenticated and not is_public:
            return redirect(f"{login_url}?next={request.path}")

        return self.get_response(request)
