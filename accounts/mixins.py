from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied

class RoleRequiredMixin:
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        #  Not logged in
        if not request.user.is_authenticated:
            return redirect("login")

        #  Role not allowed
        if request.user.role not in self.allowed_roles:
            raise PermissionDenied  # or redirect("login")

        return super().dispatch(request, *args, **kwargs)