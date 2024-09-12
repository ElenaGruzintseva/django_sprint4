from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404
from django.db.models.query import QuerySet
from django.db.models import Count
from django.utils import timezone
from django.urls import reverse, reverse_lazy
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

    def get_queryset(self):
        self.author = get_object_or_404(
            User,
            username=self.kwargs['username']
        )
        author_posts = annotate_post((
            'author',
            'location',
            'category',
        )
        )
        if self.request.user != self.author:
            return published_filter(author_posts)
        return author_posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.author
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

    def get_user(self):
        return {'username': self.request.user}

    def form_valid(self, form):
        form.instance.author = self.get_user()
        return super().form_valid(form)

    def get_success_url(self, *kwargs):
        return reverse('blog:profile', kwargs=self.get_user())


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'
    queryset = annotate_post((Post.objects.all()))

    def get_object(self):
        post = super().get_object_or_404(queryset=annotate_post((Post.objects.all())))
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
        category = get_object_or_404(
            Category, slug=self.kwargs['category_slug'],
            is_published=True)
        return category

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


class RegistrationView(CreateView):
    template_name = 'registration/registration_form.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('blog:index')
