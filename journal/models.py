from decimal import Decimal
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.core.exceptions import ValidationError


class JournalEntryQuerySet(models.QuerySet):
    def active(self):
        return self.filter(deleted_at__isnull=True)


class JournalEntry(models.Model):
    """Main ledger record for accounting/financial journal entries."""
    objects = JournalEntryQuerySet.as_manager()
    ENTRY_TYPES = [
        ('sale', 'Sales'),
        ('expense', 'Expense'),
    ]
    date = models.DateField()
    reference = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    entry_type = models.CharField(
        max_length=20,
        choices=ENTRY_TYPES,
        default='sale'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='created_entries'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='updated_entries'
    )

    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name_plural = 'Journal entries'

    def __str__(self):
        ref = f" ({self.reference})" if self.reference else ""
        return f"{self.date}{ref}: {self.description[:50]}"

    @property
    def total_debit(self):
        return sum(line.debit for line in self.lines.all())

    @property
    def total_credit(self):
        return sum(line.credit for line in self.lines.all())

    def clean(self):
        super().clean()
        if self.pk:
            total_debit = sum(
                line.debit for line in self.lines.all()
            )
            total_credit = sum(
                line.credit for line in self.lines.all()
            )
            if total_debit != total_credit:
                raise ValidationError(
                    f"Debits ({total_debit}) must equal credits ({total_credit})"
                )


class JournalEntryLine(models.Model):
    """Debit/Credit line for double-entry bookkeeping."""
    entry = models.ForeignKey(
        JournalEntry,
        on_delete=models.CASCADE,
        related_name='lines'
    )
    account = models.CharField(max_length=200)
    debit = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00')
    )
    credit = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00')
    )
    memo = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.account}: Dr {self.debit} Cr {self.credit}"

    def clean(self):
        super().clean()
        if self.debit < 0 or self.credit < 0:
            raise ValidationError("Debit and credit amounts must be non-negative.")
        if self.debit > 0 and self.credit > 0:
            raise ValidationError("A line cannot have both debit and credit amounts.")


class ActivityLog(models.Model):
    """Log for create, update, delete actions on journal entries."""
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('deleted', 'Deleted'),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    timestamp = models.DateTimeField(auto_now_add=True)
    extra = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']


class ApprovalRequest(models.Model):
    """Pending update/delete requests requiring Admin/Manager approval after 12h."""
    ACTION_CHOICES = [
        ('update', 'Update'),
        ('delete', 'Delete'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    entry = models.ForeignKey(JournalEntry, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='approval_requests_made'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='approval_requests_approved'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    payload = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']


class UserRequest(models.Model):
    """Manager-created user request; Admin approves and creates User."""
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('staff', 'Staff'),
        ('viewer', 'Viewer'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_requests_made'
    )
    username = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    password = models.CharField(max_length=128, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='user_requests_approved'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
