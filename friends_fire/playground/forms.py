
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Post, Comment


class SignUpForm(UserCreationForm):
	class Meta:
		model = User
		fields = ('username', 'email', 'password1', 'password2')

class AddPostForm(forms.ModelForm):
	class Meta:
		model = Post
		fields = ('title', 'content')


class CommentForm(forms.ModelForm):
	class Meta:
		model = Comment
		fields = ('cmnt',)


class LyricsQueryForm(forms.Form):
	song_title = forms.CharField()
	artist_name = forms.CharField()
