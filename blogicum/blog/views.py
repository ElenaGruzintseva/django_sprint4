from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.db.models import Count
from django.utils import timezone
from django.urls import reverse
from django.views.generic import (
    DeleteView, DetailView, CreateView, ListView, UpdateView
)

from .models import Category, Post, User
from .forms import CommentForm, PostForm
from .constants import PAGINATOR
from .mixins import CommentMixin, OnlyAuthorMixin, PostMixin


def published_filter(queryset):
    return queryset.filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True
    )


def annotate_post(queryset):
    return queryset.select_related('category', 'author', 'location').annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')


class ProfileUserView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = PAGINATOR

    def get_profile_user(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_queryset(self):
        posts = annotate_post(Post.objects.filter(
            author=self.get_profile_user()
        ))
        if self.request.user != self.get_profile_user():
            posts = published_filter(posts)
        return posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_profile_user()
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    fields = (
        'username',
        'first_name',
        'last_name',
        'email',
    )

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.get_object().username}
        )


class PostListView(ListView):
    model = Post
    form_class = PostForm
    template_name = 'blog/index.html'
    paginate_by = PAGINATOR
    queryset = annotate_post(published_filter(Post.objects.all()))


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={'username': self.request.user.username}
        )


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self):
        post = get_object_or_404(annotate_post(
            (Post.objects.all())), pk=self.kwargs.get(self.pk_url_kwarg))
        if post.author == self.request.user:
            return post
        return get_object_or_404(published_filter((Post.objects.all())),
                                 pk=self.kwargs.get(self.pk_url_kwarg))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related(
            'author'
        )
        return context


class PostEditView(PostMixin, UpdateView):
    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class PostDeleteView(PostMixin, DeleteView):
    pass


class CategoryPostsView(ListView):
    template_name = 'blog/category.html'
    paginate_by = PAGINATOR

    def get_category(self, **kwargs):
        return get_object_or_404(
            Category, slug=self.kwargs['category_slug'],
            is_published=True
        )

    def get_queryset(self):
        return annotate_post(published_filter(self.get_category().posts))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_category()
        return context


class CommentAddView(CommentMixin, CreateView):
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post.objects.all(),
                                               pk=self.kwargs['post_id'])
        return super().form_valid(form)


class CommentEditView(CommentMixin, OnlyAuthorMixin, UpdateView):
    pass


class CommentDeleteView(CommentMixin, OnlyAuthorMixin, DeleteView):
    pass
