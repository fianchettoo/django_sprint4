from django import forms
from django.contrib.auth import get_user_model
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'cols': 5}),
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }


User = get_user_model()


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
