from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

# for singnal stuffs
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class Course(models.Model):
	semester_or_year = (
		('1', '1st'),
		('2', '2nd'),
		('3', '3rd'),
		('4', '4th'),
		('5', '5th'),
		('6', '6th'),
		('7', '7th'),
		('8', '8th'),
	)
	course_code = models.CharField(max_length=50)
	course_title = models.CharField(max_length=200)
	semester = models.CharField(max_length=10, choices=semester_or_year, default='1')
	created_by = models.ForeignKey(User, on_delete=models.CASCADE)

	def __str__(self):
		return f'{self.course_title} - ({self.course_code})'


class Post(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	course = models.ForeignKey(Course, on_delete=models.CASCADE)
	content = models.TextField()

	def get_absolute_url(self):
		return reverse('post_details', args=[self.id])		


class Comment(models.Model):
	cmnt = models.TextField()
	user = models.ForeignKey(User, on_delete = models.CASCADE, default=1)
	post = models.ForeignKey(Post, on_delete = models.CASCADE, default=1)


class PostVote(models.Model):
	post = models.ForeignKey(Post, on_delete = models.CASCADE, default=1)
	user = models.ForeignKey(User, on_delete = models.CASCADE, default=1)
	vote_value = models.IntegerField()


class CommentVote(models.Model):
	comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
	user = models.ForeignKey(User, on_delete = models.CASCADE)
	vote_value = models.IntegerField()


## custom profile
class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	major_list = (
		('cse', 'Computer Science & Engineering'),
		('eee', 'Electricals & Electronics Engineering'),
	)
	major = models.CharField(max_length=10, choices=major_list, default='cse')
	semester_or_year = (
		('1', '1st'),
		('2', '2nd'),
		('3', '3rd'),
		('4', '4th'),
		('5', '5th'),
		('6', '6th'),
		('7', '7th'),
		('8', '8th'),
	)

	current_semester = models.CharField(max_length=10, choices=semester_or_year, default='1')
	birth_date = models.DateField(null=True, blank=True,)
	bio = models.TextField(max_length=500, blank=True)
	dp = models.ImageField(default='default.jpg', upload_to='profile_pics')
	

	def __str__(self):
		return f'{self.user.username} profile'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
	instance.profile.save

