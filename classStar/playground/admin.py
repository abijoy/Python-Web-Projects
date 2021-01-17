from django.contrib import admin
from .models import Profile
from .models import Course
from .models import Post
# Register your models here.

admin.site.register(Profile)
admin.site.register(Course)
admin.site.register(Post)