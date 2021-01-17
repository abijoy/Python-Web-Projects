from  django import forms
from .models import Profile, Post, Course, Comment
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class DateInput(forms.DateInput):
    input_type = 'date'

class ProfileForm(forms.ModelForm):
	class Meta:
		model = Profile 
		fields = ('major', 'current_semester', 'birth_date', 'bio', 'dp')
		widgets = {
			'birth_date': DateInput()
		}

class UpdateUserForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ('first_name', 'last_name', 'email')

class SignUpForm(UserCreationForm):
	class Meta:
		model = User
		fields = ('username', 'email', 'password1', 'password2')


class makePostForm(forms.ModelForm):
	class Meta:
		model = Post
		fields = ('course', 'content')

	def __init__(self, user, *args, **kwargs):
		super(makePostForm, self).__init__(*args, **kwargs)
		self.fields['course'].queryset = Course.objects.filter(semester=user.profile.current_semester)


class CommentForm(forms.ModelForm):
	class Meta:
		model = Comment
		fields = ('cmnt',)
