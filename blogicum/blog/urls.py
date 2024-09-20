from django.urls import path

from . views import (
    CategoryPostsView, CommentAddView, CommentEditView, CommentDeleteView,
    PostCreateView, PostDetailView, PostListView, PostEditView,
    PostDeleteView, ProfileUserView, ProfileUpdateView
)


app_name = 'blog'

urlpatterns = [
    path('posts/<int:post_id>/', PostDetailView.as_view(),
         name='post_detail'),
    path('category/<slug:category_slug>/', CategoryPostsView.as_view(),
         name='category_posts'),
    path('', PostListView.as_view(),
         name='index'),
    path('posts/create/', PostCreateView.as_view(),
         name='create_post'),
    path('posts/<int:post_id>/edit/', PostEditView.as_view(),
         name='edit_post'),
    path('posts/<int:post_id>/delete/', PostDeleteView.as_view(),
         name='delete_post'),
    path('profile/edit/', ProfileUpdateView.as_view(),
         name='edit_profile'),
    path('profile/<username>/', ProfileUserView.as_view(),
         name='profile'),
    path('posts/<int:post_id>/comment/', CommentAddView.as_view(),
         name='add_comment'),
    path('posts/<int:post_id>/edit_comment/<int:comment_id>/',
         CommentEditView.as_view(), name='edit_comment'),
    path('posts/<int:post_id>/delete_comment/<int:comment_id>/',
         CommentDeleteView.as_view(), name='delete_comment'),
]
