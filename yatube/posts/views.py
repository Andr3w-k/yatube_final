from django.conf import settings
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User


def authorized_only(func):
    def check_user(request, *args, **kwargs):
        if request.user.is_authenticated:
            return func(request, *args, **kwargs)
        return redirect('/auth/login/')
    return check_user


def index(request):
    posts = Post.objects.all()[:settings.POSTS_PER_PAGE]

    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.POSTS_PER_PAGE)

    template = 'posts/index.html'
    title = 'Последние обновления на сайте'

    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)
    context = {
        'title': title,
        'posts': posts,
        'page_obj': page_obj
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.group.all()[:settings.POSTS_PER_PAGE]
    template = 'posts/group_list.html'
    title = f'Записи сообщества {group}'
    post_list = group.group.all()
    paginator = Paginator(post_list, settings.POSTS_PER_PAGE)

    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)
    context = {
        'slug': slug,
        'group': group,
        'posts': posts,
        'title': title,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=author)
    paginator = Paginator(post_list, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    user = request.user.is_authenticated
    following = Follow.objects.filter(author__following__user=user)
    context = {
        'author': author,
        'page_obj': page_obj,
        'post_list': post_list,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm()
    comment = Comment.objects.filter(post=post_id)
    context = {
        'post': post,
        'form': form,
        'comment': comment,
    }
    return render(request, template, context)


@authorized_only
def post_create(request):
    template = 'posts/create_post.html'
    groups = Group.objects.all()
    form = PostForm(request.POST or None)

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect(
            'posts:profile', username=request.user.username,
        )
    else:
        form = PostForm(files=request.FILES or None)
    context = {
        'form': form,
        'groups': groups,
    }
    return render(request, template, context)


@authorized_only
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)
    groups = Group.objects.all()
    author = post.author.username
    is_edit = True
    form = PostForm(
        request.POST or None, instance=post, files=request.FILES or None
    )

    if request.user.username == author:
        if form.is_valid():
            post.save()
            return redirect('posts:post_detail', post_id=post.pk)
    context = {
        'form': form,
        'is_edit': is_edit,
        'groups': groups,
    }
    return render(request, template, context)


@authorized_only
def add_comment(request, post_id):
    template = 'posts:post_detail'
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect(template, post_id=post_id)


@authorized_only
def follow_index(request):
    # информация о текущем пользователе доступна в переменной request.user
    template = 'posts/follow.html'

    all_posts = Post.objects.filter(author__following__user=request.user)

    paginator = Paginator(all_posts, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj
    }
    return render(request, template, context)


@authorized_only
def profile_follow(request, username):
    # Подписаться на автора
    template = 'posts:profile'
    author = get_object_or_404(User, username=username)
    user = request.user
    if request.user != author:
        Follow.objects.get_or_create(user=user, author=author)
    return redirect(template, username)


@authorized_only
def profile_unfollow(request, username):
    # Дизлайк, отписка
    template = 'posts:profile'
    author = get_object_or_404(User, username=username)
    user = request.user
    if request.user != author:
        Follow.objects.filter(user=user, author=author).delete()
    return redirect(template, username)
