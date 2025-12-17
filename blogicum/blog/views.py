from django.shortcuts import render, get_object_or_404, redirect
from blog.models import Post, Category, Comment
from django.db.models import Q, Count
import datetime
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy

from django.views.generic import (
    CreateView, DeleteView, DetailView, UpdateView
)

from django.core.paginator import Paginator

from .forms import PostForm, UserForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from django.contrib.auth.mixins import LoginRequiredMixin


def index(request):
    template = 'blog/index.html'
    current_time = datetime.datetime.now()
    posts = Post.objects.select_related(
        'author'
    ).filter(
        Q(is_published=True)
        & Q(category__is_published=True)
        & Q(pub_date__lte=current_time)
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'page_obj': page_obj}

    return render(request, template, context)


class PostDetailView(DetailView):
    model = Post
    pk_url_kwarg = 'id'
    template_name = 'blog/detail.html'

    def get_queryset(self):
        current_time = datetime.datetime.now()
        user = self.request.user
        qs = Post.objects.select_related('author', 'category', 'location')

        public_posts = qs.filter(
            Q(is_published=True)
            & Q(category__is_published=True)
            & Q(pub_date__lte=current_time)
        )

        if user.is_authenticated:
            return public_posts | qs.filter(author=user)

        return public_posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context


def category_posts(request, category_slug):
    current_time = datetime.datetime.now()
    template = 'blog/category.html'
    category = get_object_or_404(
        Category.objects.filter(
            Q(slug=category_slug)
            & Q(is_published=True)
        )
    )

    posts = Post.objects.select_related(
        'category'
    ).filter(
        Q(is_published=True)
        & Q(category__slug=category.slug)
        & Q(pub_date__lte=current_time)
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'category': category,
        'page_obj': page_obj
    }
    return render(request, template, context)


User = get_user_model()


class UserDetailView(DetailView):
    model = User
    slug_field = 'username'
    slug_url_kwarg = 'username'
    template_name = 'blog/profile.html'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        current_time = datetime.datetime.now()
        context = super().get_context_data(**kwargs)
        profile_user = self.object

        visitor = self.request.user
        is_owner = visitor.is_authenticated and (
            visitor == profile_user or visitor.is_staff
        )

        if is_owner:
            posts = Post.objects.select_related(
                'author'
            ).filter(
                author=profile_user
            ).annotate(
                comment_count=Count('comments')
            ).order_by('-pub_date')
        else:
            posts = (
                Post.objects.select_related('author')
                .filter(
                    Q(author=profile_user)
                    & Q(is_published=True)
                    & Q(category__is_published=True)
                    & Q(pub_date__lte=current_time)
                ).annotate(
                    comment_count=Count('comments')
                ).order_by('-pub_date')
            )

        paginator = Paginator(posts, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['page_obj'] = page_obj
        return context


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    slug_field = 'username'
    slug_url_kwarg = 'username'
    template_name = 'blog/user.html'
    form_class = UserForm

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostMixin:
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm


class PostCreateView(LoginRequiredMixin, PostMixin, CreateView):
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostUpdateView(PostMixin, UpdateView):
    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'id': self.object.pk}
        )

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user:
            return redirect('blog:post_detail', id=post.pk)
        return super().dispatch(request, *args, **kwargs)


class PostDeleteView(PostMixin, DeleteView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class(instance=self.object)
        return context

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user:
            return redirect('blog:post_detail', id=post.pk)
        return super().dispatch(request, *args, **kwargs)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
    return redirect('blog:post_detail', id=post.pk)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(
        Comment,
        pk=comment_id,
        post__pk=post_id
    )

    if comment.author != request.user and not request.user.is_staff:
        raise PermissionDenied

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', id=post_id)
    else:
        form = CommentForm(instance=comment)

    context = {
        'form': form,
        'comment': comment
    }
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(
        Comment, pk=comment_id,
        post__pk=post_id
    )

    if comment.author != request.user and not request.user.is_staff:
        raise PermissionDenied

    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', id=post_id)

    context = {
        'comment': comment
    }
    return render(request, 'blog/comment.html', context)
