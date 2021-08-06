from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post

User = get_user_model()


@cache_page(20, key_prefix='index_page')
@require_http_methods(['GET'])
def index(request):
    posts = Post.objects.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page}
    return render(request, 'posts/index.html', context)


@require_http_methods(['GET'])
def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page, 'group': group}
    return render(request, 'posts/group.html', context)


@require_http_methods(['GET'])
def profile(request, username):
    page_author = get_object_or_404(User, username=username)
    posts = page_author.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=page_author).exists()
    context = {
        'page': page, 'author': page_author, 'following': following
    }
    return render(request, 'posts/profile.html', context)


@require_http_methods(['GET'])
def post_view(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    form = CommentForm(request.POST or None)
    comments = Comment.objects.filter(post_id=post_id)
    context = {
        'post': post,
        'author': post.author,
        'form': form,
        'comments': comments
    }
    return render(request, 'posts/post.html', context)


@require_http_methods(['GET', 'POST'])
@login_required
def new_post(request):
    edit = False
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('index')
    context = {'form': form, 'edit': edit}
    return render(request, 'posts/new_post.html', context)


@require_http_methods(['GET', 'POST'])
@login_required
def post_edit(request, username, post_id):
    edit = True
    post = get_object_or_404(Post, author__username=username, id=post_id)
    if request.user != post.author:
        return redirect('post', username=username, post_id=post_id)

    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post
    )

    if form.is_valid():
        form.save()
        return redirect('post', username=username, post_id=post_id)

    context = {'form': form, 'edit': edit, 'post': post}
    return render(request, 'posts/new_post.html', context)


@require_http_methods(['GET', 'POST'])
@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('post', username=username, post_id=post_id)
    context = {'form': form}
    return render(request, 'includes/comments.html', context)


@require_http_methods(['GET'])
@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page, 'paginator': paginator}
    return render(request, 'posts/follow.html', context)


@require_http_methods(['GET'])
@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('profile', username=username)


@require_http_methods(['GET'])
@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follow = get_object_or_404(Follow.objects.filter(
        user=request.user, author=author
    ))
    follow.delete()
    return redirect('profile', username=username)
