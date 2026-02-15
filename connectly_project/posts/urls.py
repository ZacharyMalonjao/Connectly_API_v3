from django.urls import path
from .views import UserListCreate, PostListCreate, PostDetailView, LoginView, ProtectedView, CreatePostView, PostCommentsView, CreatePostCommentView, PostLikeView, PostLikesListView

urlpatterns = [
    #utilities
    path('login/', LoginView.as_view(), name='login'),
    path('protected/', ProtectedView.as_view(), name='protected-view'),
    path('users/', UserListCreate.as_view(), name='user-list-create'),
    #Posts
    path('', PostListCreate.as_view(), name='post-list'),
    path('create/', CreatePostView.as_view(), name='create-post'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),

    #Comments
    path('<int:post_id>/comments/', PostCommentsView.as_view(), name='post-comments'),
    path('posts/<int:post_id>/comment/', CreatePostCommentView.as_view(), name='create-post-comment'),

    #Likes
    path('posts/<int:post_id>/like/', PostLikeView.as_view(), name='post-like'),
    path('posts/<int:post_id>/likes/', PostLikesListView.as_view(), name='post-likes-list'),
]
#index
#1. login
#2. users
#3. get post
#4. comments
#5. create post
#6. auth
#7. individual posts