from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods

from .forms import CommentForm, PostForm
from .models import Comment, Group, Post

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
    context = {'page': page, 'page_author': page_author}
    return render(request, 'posts/profile.html', context)


@require_http_methods(['GET'])
def post_view(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, pk=post_id)
    comments = Comment.objects.filter(post_id=post_id)
    form = CommentForm(request.POST or None)
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

    context = {'form': form, 'edit': edit}
    return render(request, 'posts/new_post.html', context)


@require_http_methods(['GET'])
def page_not_found(request, exception):
    context = {'path': request.path}
    return render(request, 'misc/404.html', context, status=404)


@require_http_methods(['GET'])
def server_error(request):
    return render(request, 'misc/500.html', status=500)


@require_http_methods(['GET', 'POST'])
@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect(
            'post', username=post.author.username, post_id=post_id
        )
    context = {'form': form}
    return render(request, 'posts/comments.html', context)
