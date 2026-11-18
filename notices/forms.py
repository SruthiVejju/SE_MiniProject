from django import forms
from core.validators import clean_text_field
from hostel.models import Room
from .models import Notice


class NoticeForm(forms.ModelForm):
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'placeholder': 'e.g., Annual Hostel Maintenance Schedule'})
    )
    content = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 6, 'placeholder': 'Detailed announcement or instructions...'})
    )
    target_block = forms.ChoiceField(
        required=False,
        label="Target Audience",
        help_text="Select 'All Students' to broadcast everywhere, or choose a specific block."
    )

    class Meta:
        model = Notice
        fields = ['title', 'content', 'target_block']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [('', 'All Students (General Announcement)')]
        blocks = (
            Room.objects.values_list('block', flat=True)
            .distinct()
            .order_by('block')
        )
        for block in blocks:
            if block:
                choices.append((block, f'Block {block} Residents Only'))
        self.fields['target_block'].choices = choices

    def clean_title(self):
        return clean_text_field(self.cleaned_data.get('title'), 'Title', min_len=3, max_len=200)

    def clean_content(self):
        return clean_text_field(self.cleaned_data.get('content'), 'Content', min_len=5, max_len=5000)
