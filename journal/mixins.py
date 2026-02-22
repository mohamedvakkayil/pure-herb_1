"""Mixins for view protection and role-based access."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


def user_in_role(user, role):
    """Check if user has the given role (admin, manager, staff, viewer)."""
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    group_names = [g.name.lower() for g in user.groups.all()]
    if role == 'admin':
        return 'admin' in group_names
    if role == 'manager':
        return 'manager' in group_names or 'admin' in group_names
    if role == 'staff':
        return 'staff' in group_names or 'manager' in group_names or 'admin' in group_names
    if role == 'viewer':
        return any(r in group_names for r in ['viewer', 'staff', 'manager', 'admin'])
    return False


class RoleRequiredMixin(LoginRequiredMixin):
    """Require user to have one of the allowed roles."""
    allowed_roles = ['admin', 'manager', 'staff', 'viewer']

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        has_role = any(user_in_role(request.user, r) for r in self.allowed_roles)
        if not has_role:
            raise PermissionDenied('You do not have permission to access this page.')
        return super().dispatch(request, *args, **kwargs)
