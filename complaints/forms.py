from django import forms

from core.validators import clean_text_field

from .models import Complaint


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['category', 'description']
        labels = {
            'category': 'Complaint Category',
            'description': 'Describe the Problem',
        }
        help_texts = {
            'category': 'Choose the category that best matches your issue.',
            'description': (
                'Explain the problem clearly. '
                'Enter between 10 and 500 characters.'
            ),
        }
        widgets = {
            'category': forms.Select(attrs={
                'class': 'form-control',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'maxlength': 500,
                'placeholder': (
                    'Example: The lights in my room are not working.'
                ),
            }),
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