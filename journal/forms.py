from decimal import Decimal
from django import forms
from django.forms import inlineformset_factory

from .mixins import user_in_role
from .models import JournalEntry, JournalEntryLine, UserRequest


class JournalEntryForm(forms.ModelForm):
    """Form for JournalEntry (date, reference, description)."""
    class Meta:
        model = JournalEntry
        fields = ['date', 'reference', 'description', 'entry_type']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'reference': forms.TextInput(attrs={'placeholder': 'e.g. INV-001', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'placeholder': 'Entry description...', 'class': 'form-control', 'rows': 3}),
        }


class JournalEntryLineForm(forms.ModelForm):
    """Form for a single journal entry line."""
    class Meta:
        model = JournalEntryLine
        fields = ['account', 'debit', 'credit', 'memo']
        widgets = {
            'account': forms.TextInput(attrs={'placeholder': 'e.g. Cash, Revenue', 'class': 'form-control'}),
            'debit': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'placeholder': '0.00', 'class': 'form-control'}),
            'credit': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'placeholder': '0.00', 'class': 'form-control'}),
            'memo': forms.TextInput(attrs={'placeholder': 'Optional memo', 'class': 'form-control'}),
        }

    def clean(self):
        cleaned = super().clean()
        debit = cleaned.get('debit') or Decimal('0')
        credit = cleaned.get('credit') or Decimal('0')
        if debit < 0 or credit < 0:
            raise forms.ValidationError("Amounts must be non-negative.")
        if debit > 0 and credit > 0:
            raise forms.ValidationError("A line cannot have both debit and credit.")
        return cleaned


class BaseJournalEntryLineFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        total_debit = Decimal('0')
        total_credit = Decimal('0')
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE'):
                total_debit += form.cleaned_data.get('debit') or Decimal('0')
                total_credit += form.cleaned_data.get('credit') or Decimal('0')
        if total_debit != total_credit:
            raise forms.ValidationError(
                f"Total debits ({total_debit}) must equal total credits ({total_credit})."
            )


class SalesForm(forms.Form):
    """Simplified form for recording a sale."""
    PAYMENT_CHOICES = [('cash', 'Cash'), ('card', 'Card')]
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    amount = forms.DecimalField(max_digits=14, decimal_places=2, min_value=0)
    payment_method = forms.ChoiceField(
        choices=PAYMENT_CHOICES,
        widget=forms.RadioSelect,
        initial='cash'
    )
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))
    reference = forms.CharField(required=False, max_length=100)


class ExpenseForm(forms.Form):
    """Simplified form for recording an expense."""
    PAYMENT_CHOICES = [('cash', 'Cash'), ('card', 'Card')]
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    amount = forms.DecimalField(max_digits=14, decimal_places=2, min_value=0)
    payment_method = forms.ChoiceField(
        choices=PAYMENT_CHOICES,
        widget=forms.RadioSelect,
        initial='cash'
    )
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))
    category = forms.CharField(max_length=100)
    reference = forms.CharField(required=False, max_length=100)


class UserRequestForm(forms.ModelForm):
    """Form for Manager to request a new user (Admin approves)."""
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Temporary password'}))

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._requesting_user = user
        if user and not user_in_role(user, 'admin'):
            self.fields['role'].choices = [('staff', 'Staff'), ('viewer', 'Viewer')]

    def clean_role(self):
        role = self.cleaned_data.get('role')
        user = self._requesting_user
        if user and not user_in_role(user, 'admin') and role in ('admin', 'manager'):
            raise forms.ValidationError('You cannot request Admin or Manager roles.')
        return role

    class Meta:
        model = UserRequest
        fields = ['username', 'email', 'role', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email (optional)'}),
        }

    def save(self, commit=True):
        obj = super().save(commit=False)
        # Store plain password for Admin to use when creating user on approve
        obj.password = self.cleaned_data.get('password', '')
        if commit:
            obj.save()
        return obj


class UserResetPasswordForm(forms.Form):
    """Form for admin to reset a user's password."""
    password1 = forms.CharField(
        label='New password',
        widget=forms.PasswordInput(attrs={'placeholder': 'New password', 'autocomplete': 'new-password'})
    )
    password2 = forms.CharField(
        label='Confirm password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm password', 'autocomplete': 'new-password'})
    )

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Passwords do not match.')
        return cleaned


JournalEntryLineFormSet = inlineformset_factory(
    JournalEntry,
    JournalEntryLine,
    form=JournalEntryLineForm,
    formset=BaseJournalEntryLineFormSet,
    extra=2,
    min_num=2,
    validate_min=True,
    can_delete=True,
)
