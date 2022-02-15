from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from pytz import timezone
from .models import Post, Group, User
from .forms import PostForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)

    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_list(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.filter(group=group)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'text': slug,
        'group': group,
    }
    return render(request, template, context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.select_related('author', 'group').filter(
        author__username=user)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'author': user,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    number_of_posts = Post.objects.count()

    context = {
        'post': post,
        'number_of_posts': number_of_posts,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)

    if not form.is_valid():
        context = {'form': form}
        return render(request, 'posts/create_post.html', context)

    post = form.save(commit=False)
    post.author = request.user
    post.pub_date = timezone.now()
    post.save()
    username = request.user.username
    return redirect('posts:profile', username=username)


def post_edit(request, post_id):
    if request.method == 'GET':
        post = get_object_or_404(Post, pk=post_id)
        form = PostForm(instance=post)
        if post.author.id == request.user.id:
            context = {'form': form,
                       'is_edit': True,
                       'post_id': post_id}
            return render(request, 'posts/create_post.html', context)
        else:
            return redirect('posts:post_detail', post_id=post_id)

    elif request.method == 'POST':
        post = get_object_or_404(Post, pk=post_id)
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.pub_date = timezone.now()
            post.save()
            return redirect('posts:post_detail', post_id=post.pk)
