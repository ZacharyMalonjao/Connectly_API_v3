from django.urls import path
from .views import UserListCreate, PostListCreate, PostDetailView, CommentListCreate, LoginView, ProtectedView, CreatePostView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('users/', UserListCreate.as_view(), name='user-list-create'),
    path('', PostListCreate.as_view(), name='post-list'),
    path('comments/', CommentListCreate.as_view(), name='comment-list-create'),
    path('posts/create/', CreatePostView.as_view(), name='create-post'),
    path('protected/', ProtectedView.as_view(), name='protected-view'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),

]
#index
#1. login
#2. users
#3. get post
#4. comments
#5. create post
#6. auth