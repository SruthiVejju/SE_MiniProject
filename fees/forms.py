import re

from django import forms

from core.validators import sanitize_text

from .models import FeeAccount, FeePayment


class PaymentForm(forms.Form):
    account = forms.ModelChoiceField(queryset=FeeAccount.objects.none(), label='Student')
    amount = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)
    mode = forms.ChoiceField(choices=FeePayment.MODE_CHOICES)
    reference = forms.CharField(max_length=64, required=False, label='Gateway reference')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['account'].queryset = FeeAccount.objects.select_related('student')

    def clean_reference(self):
        ref = sanitize_text(self.cleaned_data.get('reference', ''))
        if ref and not re.fullmatch(r'[A-Za-z0-9_\-]{1,64}', ref):
            raise forms.ValidationError('Reference may only contain letters, digits, - and _.')
        return ref

    def clean(self):
        data = super().clean()
        if data.get('mode') == FeePayment.ONLINE and not data.get('reference'):
            self.add_error('reference', 'Online payments require a gateway reference.')
        return data
