"""Context processors for global template context."""

from .mixins import user_in_role
from .models import ApprovalRequest, UserRequest


def sidebar(request):
    """Provide sidebar nav data: counts and visibility flags."""
    if not request.user.is_authenticated:
        return {}

    show_approval_queue = user_in_role(request.user, 'admin') or user_in_role(request.user, 'manager')
    show_user_approval = user_in_role(request.user, 'admin')
    show_user_management = user_in_role(request.user, 'admin')

    result = {
        'show_approval_queue': show_approval_queue,
        'show_user_approval': show_user_approval,
        'show_user_management': show_user_management,
        'sidebar_approval_count': 0,
        'sidebar_user_requests_count': 0,
    }

    if show_approval_queue:
        result['sidebar_approval_count'] = ApprovalRequest.objects.filter(status='pending').count()

    if show_user_approval:
        result['sidebar_user_requests_count'] = UserRequest.objects.filter(status='pending').count()

    return result
