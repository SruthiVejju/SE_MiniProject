from django import forms
from django.utils import timezone

from core.validators import clean_text_field

from .models import LeaveRequest


class LeaveRequestForm(forms.ModelForm):
    from_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    to_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = LeaveRequest
        fields = ['destination', 'from_date', 'to_date', 'reason']

    def clean_destination(self):
        return clean_text_field(self.cleaned_data['destination'], 'Destination', 2, 100)

    def clean_reason(self):
        return clean_text_field(self.cleaned_data['reason'], 'Reason', 10, 500)

    def clean(self):
        data = super().clean()
        start, end = data.get('from_date'), data.get('to_date')
        if start and start < timezone.localdate():
            self.add_error('from_date', 'From-date cannot be in the past.')
        if start and end and end < start:
            self.add_error('to_date', 'To-date cannot be before from-date.')
        return data
