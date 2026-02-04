from django.urls import path
from .views import UserListCreate, PostListCreate, CommentListCreate, LoginView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('users/', UserListCreate.as_view(), name='user-list-create'),
    path('', PostListCreate.as_view(), name='post-list-create'),
    path('comments/', CommentListCreate.as_view(), name='comment-list-create'),
]
#test comment