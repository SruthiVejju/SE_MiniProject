from django import forms

from core.validators import clean_text_field

from .models import Complaint


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['category', 'description']
        widgets = {
            'category': forms.Select(),
            'description': forms.Textarea(attrs={'rows': 5}),
        }

    def clean_description(self):
        return clean_text_field(
            self.cleaned_data['description'],
            'Description',
            10,
            500
        )

class ComplaintUpdateForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['status', 'remark']
        widgets = {
            'remark': forms.Textarea(attrs={'rows': 3}),
        }