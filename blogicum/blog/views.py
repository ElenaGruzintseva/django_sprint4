from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.db.models.query import QuerySet
from django.db.models import Count
from django.views.generic import (
    DeleteView, DetailView, CreateView, ListView, UpdateView)
from django.utils import timezone
from django.urls import reverse, reverse_lazy
from .models import Category, Comment, Post, User
from .forms import CommentForm, PostForm


class PostCommentDispatchView():
    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


class DetailMixin():
    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentMixin(DetailMixin):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'
    form_class = CommentForm


def filter_posts(
    queryset: QuerySet = Post.objects.all(),
    apply_filters: bool = True
):
    if apply_filters:
        queryset = queryset.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True
        )

    queryset = queryset.select_related('category').annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')

    return queryset


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class ProfileMixin:
    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user}
        )


class ProfileUserView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = 10

    def get_queryset(self):
        self.author = get_object_or_404(
            User,
            username=self.kwargs['username']
        )

        apply_filters = self.request.user != self.author
        return filter_posts(
            queryset=self.author.posts.select_related(
                'author',
                'location',
                'category',
            ),
            apply_filters=apply_filters
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.author
        return context


class ProfileUpdateView(LoginRequiredMixin, ProfileMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    success_url = reverse_lazy('blog:profile')
    fields = (
        'username',
        'first_name',
        'last_name',
        'email',
    )

    def get_object(self, queryset=None):
        return self.request.user


class PostListView(ListView):
    model = Post
    form_class = PostForm
    template_name = 'blog/index.html'
    paginate_by = 10

    def get_queryset(self):
        return filter_posts()


class PostCreateView(LoginRequiredMixin, ProfileMixin, CreateView):
    model = Post
    form_class = PostForm
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_queryset(self):
        return super().get_queryset().select_related(
            'author',
            'location',
            'category',
        )

    def get_object(self, queryset=None):
        post = super().get_object(queryset=queryset)
        if post.author != self.request.user:
            return get_object_or_404(filter_posts(),
                                     pk=self.kwargs.get(self.pk_url_kwarg)
                                     )
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related(
            'author'
        )
        return context


class PostEditView(DetailMixin, LoginRequiredMixin,
                   PostCommentDispatchView, UpdateView):
    model = Post
    pk_url_kwarg = 'post_id'
    form_class = PostForm
    template_name = 'blog/create.html'


class PostDeleteView(PostCommentDispatchView, DeleteView):
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')


class CategoryPostsView(ListView):
    template_name = 'blog/category.html'
    paginate_by = 10

    def get_queryset(self):
        category = get_object_or_404(
            Category, slug=self.kwargs['category_slug'], is_published=True)
        return filter_posts(
            queryset=Post.objects.filter(category=category)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category, slug=self.kwargs['category_slug'], is_published=True)
        return context


class CommentAddView(CommentMixin, LoginRequiredMixin, CreateView):
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(
            filter_posts(),
            pk=self.kwargs['post_id']
        )
        return super().form_valid(form)


class CommentEditView(CommentMixin, PostCommentDispatchView,
                      OnlyAuthorMixin, UpdateView):
    pass


class CommentDeleteView(CommentMixin, OnlyAuthorMixin, DeleteView):
    pass
