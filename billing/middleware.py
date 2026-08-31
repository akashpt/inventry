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
        if request.path in ["/users", "/users/new", "/settings"] and not UserProfile.objects.filter(role=UserProfile.MANAGEMENT, status="Active").exists():
            is_public = True

        if not request.user.is_authenticated and not is_public:
            return redirect(f"{login_url}?next={request.path}")
        if request.user.is_authenticated and not is_public and not self.has_role_access(request):
            return redirect("index")

        return self.get_response(request)

    def has_role_access(self, request):
        if request.user.is_superuser:
            return True
        profile = getattr(request.user, "userprofile", None)
        if not profile or profile.status != "Active":
            return request.path in [reverse("profile"), reverse("change_password"), reverse("logout")]
        if profile.role == UserProfile.MANAGEMENT:
            return True

        accountant_paths = (
            "/invoice", "/invoice-items", "/payments-received", "/investment", "/withdrawal",
            "/expenses", "/petty-cash", "/supplier-bills", "/customer-statement",
            "/supplier-statement", "/reports", "/profile", "/change-password", "/logout",
        )
        sales_manager_paths = (
            "/customer", "/newcustomer", "/products", "/quotations", "/quotation-items",
            "/sales-orders", "/sales-order-items", "/delivery-notes", "/delivery-note-items",
            "/invoice", "/invoice-items", "/returns", "/reports", "/profile", "/change-password", "/logout",
        )
        sales_staff_paths = (
            "/customer", "/newcustomer", "/products", "/quotations", "/quotation-items",
            "/sales-orders", "/sales-order-items", "/delivery-notes", "/delivery-note-items",
            "/returns", "/warehouse-stock", "/profile", "/change-password", "/logout",
        )
        role_paths = {
            UserProfile.ACCOUNTANT: accountant_paths,
            UserProfile.SALES_MANAGER: sales_manager_paths,
            UserProfile.SALES_STAFF: sales_staff_paths,
        }
        allowed = role_paths.get(profile.role, ())
        return request.path == "/" or any(request.path.startswith(path) for path in allowed)
