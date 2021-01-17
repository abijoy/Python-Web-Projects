from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from .models import Post, Upvote, Comment
from django.contrib.auth.models import User
from .forms import SignUpForm, AddPostForm, CommentForm, LyricsQueryForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse
from django.http import HttpResponse
from lyricsFinder import lyricsFinderAz, lyricsFinderMetro
from django.contrib import messages
from notify.signals import notify




def home(request):
	posts = Post.objects.all()
	key = lambda x: (-x.comment_set.all().count(), -x.upvote_set.all().count())
	posts = sorted(posts, key=key)
	up_posts = []
	if not request.user.is_anonymous:
		up_posts = [u.post for u in Upvote.objects.filter(user=request.user)]
		
	return render(request, 'playground/home.html',
		{'posts': posts, 'upvoted_posts': up_posts},
	)

@login_required
def post_details(request, post_id):
	p = get_object_or_404(Post, id=post_id)
	upvotes = Upvote.objects.filter(post=p).count()
	can_up = True
	if not request.user.is_anonymous:
		can_up = not p.upvote_set.filter(user=request.user).count()

	if request.method == 'POST':
		form = CommentForm(request.POST)
		if form.is_valid():
			r = form.save(commit=False)
			r.user = request.user
			r.post = get_object_or_404(Post, id=post_id)
			r.save()
			notify.send(request.user, recipient=p.author, actor=request.user, verb='commented', nf_type='sombody_commented')
			return redirect(reverse('post_details', kwargs={'post_id': post_id}))
	else:
		form = CommentForm()

	# resp1 = make_comment(request, post_id)
	resp2 = render(request, 'playground/post_details.html',
		{'post': p, 'upvotes':upvotes, 'can_up': can_up, 'form': form}
	)

	return resp2

@login_required
def upvote(request, post_id):
	p = get_object_or_404(Post, id=post_id)

	if not p.upvote_set.filter(user=request.user).count():
		up = Upvote(post=p, user=request.user)
		up.save()
		notify.send(request.user, recipient=p.author, actor=request.user, verb='upvoted', nf_type='sombody_upvoted')
	upvotes = Upvote.objects.filter(post=p).count()
	return redirect(reverse('post_details', kwargs={'post_id': p.id}))

def SignUp(request):
	if request.method == 'POST':
		print(request.POST)
		form = SignUpForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password1')
			user = authenticate(username=username, password=password)
			login(request, user)
			return redirect('/')

	else:
		form = SignUpForm()
	return render(request, 'playground/signup.html', {'form': form})

@login_required
def addPost(request):
	if request.method == 'POST':
		form = AddPostForm(request.POST)
		if form.is_valid():
			temp = form.save(commit=False)
			temp.author = request.user
			temp.save()
			up = Upvote(user=request.user, post=temp)
			up.save()
			recipient_list = list(User.objects.all())
			notify.send(request.user, recipient_list=recipient_list, actor=request.user,
				actor_text=f'{request.user.username}',
				verb='posted.', obj=temp, nf_type='somebody_posted')
			return redirect(reverse('post_details', kwargs={'post_id': temp.id})) 
	else:
		form = AddPostForm()
		return render(request, 'playground/addPost.html', {'form': form})

@login_required
def unvote(request, post_id):
	if not request.user.is_anonymous:
		post = get_object_or_404(Post, id=post_id)
		up = get_object_or_404(Upvote, user=request.user, post=post)
		up.delete()
		return redirect(reverse('post_details', kwargs={'post_id': post.id}))

def upvoted_by(request, post_id):
	post = get_object_or_404(Post, id=post_id)
	up_by = get_list_or_404(Upvote, post=post)
	return render(request, 'playground/upvoted_by.html',
		{'up_by': up_by, 'post': post}
	)

@login_required
def make_comment(request, post_id):
	p = get_object_or_404(Post, id=post_id)
	notify.send(request.user, recipient=request.user, actor=request.user, verb='commented', nf_type='sombody_commented')

	if request.method == 'POST':
		form = CommentForm(request.POST)
		if form.is_valid():
			r = form.save(commit=False)
			r.user = request.user
			r.post = p
			r.save()
			# print(recipient)
			
			return redirect(reverse('post_details', kwargs={'post_id': post_id}))
	else:
		form = CommentForm()
		return render(request, 'playground/make_comment.html',
			{'form': form, 'post': post}
		)














# def lyrics_finder(request, )

def find_lyrics(request):
	
	if request.method == 'POST':
		song_title = request.POST.get('song_title')
		artist_name = request.POST.get('artist_name')
		print(song_title, artist_name)
		title = song_title + ' - ' + artist_name
		lyrics = lyricsFinderAz(song_title, artist_name)
		credit = 'AZLyrics'
		if not lyrics:
			 lyrics = lyricsFinderMetro(song_title, artist_name)
			 credit = 'MetroLyrics'
		if not lyrics:
			messages.add_message(request, messages.ERROR, 
				'Lyrics Not Found in [AZLyrics, MetroLyrics]')
			return redirect(reverse('find_lyrics'))
		return render(request, 'playground/lyrics_found.html',
			{'lyrics': lyrics, 'title': title, 'credit': credit}
		)
	else:
		form = LyricsQueryForm()
		return render(request, 'playground/lyrics_form.html', {'form': form})


#JsonResponse testing
from django.http import JsonResponse
def post_details_json(request, pk):
	post = get_object_or_404(Post, pk=pk)
	data = {'result': {
		'title': post.title,
		'content': post.content,
		'author': post.author.username
	}}
	return JsonResponse(data)

def allPost_json(request):
	posts = Post.objects.all()
	data = {'result': list(posts.values('title', 'content', 'author__username'))}
	return JsonResponse(data)