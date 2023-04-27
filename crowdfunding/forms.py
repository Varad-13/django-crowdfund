from django import forms
from .models import Post
from django.core.validators import FileExtensionValidator

class PostForm(forms.ModelForm):
    thumbnail = forms.FileField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'input'}))
    video = forms.FileField(required=False, validators=[FileExtensionValidator(allowed_extensions=['MOV','avi','mp4','webm','mkv'])], widget=forms.ClearableFileInput(attrs={'class': 'input'}))

    class Meta:
        model = Post
        fields = ['title', 'intro', 'body', 'contribution_amount', 'thumbnail', 'video']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'input', 'placeholder': 'The title of your post', 'required': True}),
            'intro': forms.TextInput(attrs={'class': 'input', 'placeholder': 'The intro of your post', 'required': True}),
            'body': forms.Textarea(attrs={'class': 'textarea', 'placeholder': 'Include details about your cause'}),
            'contribution_amount': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Contribution amount'}),
        }
        validators = {
            'video': FileExtensionValidator(allowed_extensions=['MOV','avi','mp4','webm','mkv'])
        }
