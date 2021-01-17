from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.shortcuts import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .models import Course, Profile, Post, PostVote, Comment, CommentVote
from .forms import ProfileForm, SignUpForm, UpdateUserForm, makePostForm, CommentForm
from notify.signals import notify

# Create your views here.

@login_required
def index(request):
	# c = Course.objects.get(pk=1)
	u = request.user
	current_sem = u.profile.current_semester
	my_courses = Course.objects.filter(semester=current_sem)
	posts = Post.objects.filter(course__in=my_courses)
	upVotedPosts = [v.post for v in PostVote.objects.filter(user=request.user, vote_value=1)]
	downVotedPosts =  [v.post for v in PostVote.objects.filter(user=request.user, vote_value=-1)]
	#votes = PostVote.objects.filter(post=p, vote_value=1).count() - PostVote.objects.filter(post=p, vote_value=-1).count()
	print(upVotedPosts, downVotedPosts, posts)
	for p in posts:
		if p in upVotedPosts:
			print("Yeaaaa;")

	if request.method == 'POST':
		form = makePostForm(request.user, request.POST)
		if form.is_valid():
			f = form.save(commit=False)
			f.user = request.user
			f.save()
			recipient_list = [p.user for p in Profile.objects.filter(current_semester=request.user.profile.current_semester)]
			notify.send(request.user, recipient_list=recipient_list, actor=request.user,
			verb='posted', obj=f, target=f.course, nf_type='somebody_posted')
			return redirect(reverse('index'))
	
	else:
		form = makePostForm(request.user)
	
	return render(request, 'playground/home.html',
		{'form':form, 'my_courses': my_courses, 'posts': posts, 
		'upVotedPosts': upVotedPosts, 'downVotedPosts': downVotedPosts,}
		)


@login_required
def post_details(request, post_id):
	p = get_object_or_404(Post, id=post_id)
	postVotes = PostVote.objects.filter(post=p, vote_value=1).count() - PostVote.objects.filter(post=p, vote_value=-1).count()
	voted = True if p.postvote_set.filter(user=request.user).count() else False
	voteStatus = 1
	if voted:
		voteStatus = get_object_or_404(PostVote, user=request.user, post=p).vote_value

	if request.method == 'POST':
		form = CommentForm(request.POST)
		if form.is_valid():
			f = form.save(commit=False)
			f.user = request.user
			f.post = p
			f.save()
			return redirect(reverse('post_details', kwargs={'post_id': post_id}))
			
	else:
		form = CommentForm()

	resp = render(request, 'playground/post_details.html',
		{'post': p, 'postVotes':postVotes, 'voteStatus': voteStatus, 'form': form}
	)

	return resp


@login_required
def vote(request, post_id, status):
	p = get_object_or_404(Post, id=post_id)
	upVoter = True if p.postvote_set.filter(user=request.user, vote_value=1).count() else False
	downVoter = True if p.postvote_set.filter(user=request.user, vote_value=-1).count() else False
	if status == 'up':
		if upVoter:
			vote = get_object_or_404(PostVote, user=request.user, post=p)
			vote.delete()
		elif downVoter:
			vote = get_object_or_404(PostVote, user=request.user, post=p)
			vote.vote_value = 1
			vote.save()
		else:
			v = PostVote(post=p, user=request.user, vote_value=1)
			v.save()

	if status == 'down':
		if downVoter:
			vote = get_object_or_404(PostVote, user=request.user, post=p)
			vote.delete()
		elif upVoter:
			vote = get_object_or_404(PostVote, user=request.user, post=p)
			vote.vote_value = -1
			vote.save()
		else:
			v = PostVote(post=p, user=request.user, vote_value=-1)
			v.save()
	#votes = PostVote.objects.filter(post=p, vote_value=1).count() - PostVote.objects.filter(post=p, vote_value=-1).count()
	return redirect(reverse('post_details', kwargs={'post_id': p.id}))

def posts_under_course(request, course_code):
	course_obj = Course.objects.get(course_code=course_code)
	posts = Post.objects.filter(course=course_obj)
	u = request.user
	current_sem = u.profile.current_semester
	my_courses = Course.objects.filter(semester=current_sem)
	return render(request, 'playground/posts_list.html', {'posts': posts, 'my_courses': my_courses})

def allPost(request):
	userSems = user.profile.current_semester
	print(request.user)
	course = Course.objects.filter(semester=userSems)
	posts = Post.objects.filter(course=course)
	totalPosts = posts.count()
	return render(request, 'playground/posts_list.html', {'posts': posts, 'totalPosts': totalPosts})

def makePost(request):
	if request.method == 'POST':
		form = makePostForm(request.user, request.POST)
		if form.is_valid():
			f = form.save(commit=False)
			f.user = request.user
			f.save()
			return redirect(reverse('index'))
	
	else:
		form = makePostForm(request.user)
		return form
		#return render(request, 'playground/makePost.html', {'form':form})

def users(request):
	tmplt = '<br>'.join([f'<a href="/profile/{u.username}">{u.username}</a>' for u in User.objects.all()])
	return HttpResponse(tmplt)

def profile(request, username):
	u = User.objects.get(username=username)
	user_details = f'<img src="{u.profile.dp.url}" style="width: 100px; height: 100px"/>'
	ed = ''
	if u == request.user:
		ed = f'<a href="/edit-profile"> Edit my profile</a>'
	user_details += f'''<h3>is_superuser: {u.is_superuser} </h3> <div>Username: {u.username} <br>
	Major : {u.profile.major} <br>Semester: {u.profile.current_semester} <br>Bio: {u.profile.bio} <br>{ed}</div>'''
	return HttpResponse(user_details)

@login_required
@transaction.atomic
def edit_profile(request):
	print(request.user)
	if request.method == 'POST':
		print(request.POST)
		u_form = UpdateUserForm(request.POST, instance=request.user)
		p_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
		if u_form.is_valid() and p_form.is_valid():
			u_form.save()
			p_form.save()
			#username = form.cleaned_data.get('username')
			#password = form.cleaned_data.get('password1')
			#user = authenticate(username=username, password=password)
			#login(request, user)
			return redirect('/')

	else:
		u_form = UpdateUserForm(instance=request.user)
		p_form = ProfileForm(instance=request.user.profile)
	return render(request, 'playground/edit_profile.html', {'u_form': u_form, 'p_form': p_form})

def signup(request):
	if request.method == 'POST':
		form = SignUpForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password1')
			user = authenticate(username=username, password=password)
			login(request, user)
			return redirect('/edit-profile/')

	else:
		form = SignUpForm()
	return render(request, 'playground/signup.html', {'form': form})