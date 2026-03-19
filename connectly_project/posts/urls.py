from django.urls import path
from .views import UserListCreate, PostListCreate, PostDetailView, LoginView, ProtectedView, CreatePostView, CommentListCreateView,  PostLikeView,PostLikesListView, FeedView,CommentDetailView

urlpatterns = [
    #utilities
    path('login/', LoginView.as_view(), name='login'),
    path('protected/', ProtectedView.as_view(), name='protected-view'),
    path('users/', UserListCreate.as_view(), name='user-list-create'),
  
    #Posts
    path('', PostListCreate.as_view(), name='post-list'),
    path('create/', CreatePostView.as_view(), name='create-post'),
    path('<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    

    #Comments
    path('<int:post_id>/comments/', CommentListCreateView.as_view(), name='post-comments'),
    #path('<int:post_id>/comment/', CreatePostCommentView.as_view(), name='create-post-comment'),
    #path('<int:post_id>/comments/<int:comment_id>/delete/',DeleteCommentView.as_view(),name='delete-comment'),
    path('<int:post_id>/comments/<int:comment_id>/',CommentDetailView.as_view(),name='delete-comment'),
    
    #Likes
    path('<int:post_id>/like/', PostLikeView.as_view(), name='post-like'),
    path('<int:post_id>/likes/', PostLikesListView.as_view(), name='post-likes-list'),

    #Feed
    path('feed/', FeedView.as_view(), name='feed'),
   
]
