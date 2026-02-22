"""Utilities for activity logging."""
from django.contrib.contenttypes.models import ContentType

from .models import ActivityLog


def log_activity(user, action, obj, extra=None):
    """Log create, update, or delete action on an object."""
    if action not in ('created', 'updated', 'deleted'):
        return
    ct = ContentType.objects.get_for_model(obj)
    ActivityLog.objects.create(
        user=user,
        action=action,
        content_type=ct,
        object_id=obj.pk,
        extra=extra
    )
