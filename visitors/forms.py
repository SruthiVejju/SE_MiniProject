from django import forms
from django.contrib.auth import get_user_model

from core.models import UserProfile
from core.validators import clean_text_field


class VisitorEntryForm(forms.Form):
    name = forms.CharField(max_length=100)
    purpose = forms.CharField(max_length=200)
    host_student = forms.ModelChoiceField(queryset=get_user_model().objects.none())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['host_student'].queryset = get_user_model().objects.filter(
            profile__role=UserProfile.STUDENT).order_by('username')

    def clean_name(self):
        return clean_text_field(self.cleaned_data['name'], 'Visitor name', 2, 100)

    def clean_purpose(self):
        return clean_text_field(self.cleaned_data['purpose'], 'Purpose', 3, 200)
