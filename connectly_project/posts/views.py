#from django.utils.decorators import method_decorator
#from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import render
from django.db import models
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from .permissions import PostPrivacyPermission, IsUserOrAdmin, IsPostAuthorOrAdmin, IsAdmin
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Post, Comment
from .serializers import UserSerializer, PostSerializer, CommentSerializer
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from posts.factories.post_factory import PostFactory
from singletons.logger_singleton import LoggerSingleton
from django.contrib.auth import get_user_model
User = get_user_model()
from .models import Post, Like
from .serializers import LikeSerializer
logger = LoggerSingleton().get_logger()

from rest_framework.authtoken.models import Token
from google.oauth2 import id_token
from google.auth.transport import requests
from rest_framework.pagination import PageNumberPagination
from rest_framework.pagination import CursorPagination
from django.db.models import Q


#===================Utility views==================    
class ProtectedView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": f"Authenticated as {request.user.username}!"})

class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            logger.info(f"User '{username}' logged in successfully.")
            return Response({"message": "Authentication successful!"}, status=200)

        logger.warning(f"Failed login attempt for username '{username}'.")
        return Response({"error": "Invalid credentials"}, status=401)


class GoogleLoginView(APIView):

    def post(self, request):
        google_token = request.data.get("id_token")

        if not google_token:
            return Response(
                {"error": "No token provided"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Verify token with Google
            idinfo = id_token.verify_oauth2_token(
                google_token,
                requests.Request()
            )

            email = idinfo.get("email")

        except ValueError:
            return Response(
                {"error": "Invalid Google token"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Find or create user
        user, created = User.objects.get_or_create(
            username=email,
            defaults={"email": email}
        )

        # Generate your API token
        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                "token": token.key,
                "email": user.email
            },
            status=status.HTTP_200_OK
        )

#========================model views============
     
class UserListCreate(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  # hashed password automatically
            return Response(
                {"id": user.id, "username": user.username, "email": user.email},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#get post by pk (specific)
class PostDetailView(APIView):
    permission_classes = [IsAuthenticated, PostPrivacyPermission,IsPostAuthorOrAdmin,]
    authentication_classes = [TokenAuthentication] 
    def get(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            logger.error(f"Post {pk} not found for user '{request.user.username}'")
            return Response({"error": "Post not found"}, status=404)

        # Check object-level permissions
        try:
            self.check_object_permissions(request, post)
        except Exception as e:
            logger.warning(f"Permission denied for user '{request.user.username}' on post {pk}")
            raise e

        logger.info(f"Post {pk} retrieved by user '{request.user.username}'")
        #return Response({"id": post.id, "content": post.content, "author": post.author.username})
        serializer = PostSerializer(post)
        return Response(serializer.data)
    
    def delete(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            logger.error(f"Post {pk} not found for user '{request.user.username}'")
            return Response({"error": "Post not found"}, status=404)

        logger.info(f"Post {pk} retrieved by user '{request.user.username}'")

        try:
            self.check_object_permissions(request, post)
        except Exception as e:
            logger.warning(f"Permission denied for user '{request.user.username}' on post {pk}")
            raise e

        post.delete()
        return Response({"message": "Post deleted"}, status=204)
#create post 
class CreatePostView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        

        data = request.data
        try:
            post = PostFactory.create_post(
                post_type=data['post_type'],
                title=data['title'],
                content=data.get('content', ''),
                metadata=data.get('metadata', {})
            )
            post.author = request.user  # <-- assign author automatically
            post.save()

            
            logger.info(f"Post created successfully with ID {post.id}")
            return Response(
                {'message': 'Post created successfully!', 'post_id': post.id}, 
                status=status.HTTP_201_CREATED
                )
        except ValueError as e:
            logger.error(f"Post creation failed: {str(e)}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
                )
#get posts   
class PostListCreate(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        
        user = request.user
        if user.role == 'admin':
            posts = Post.objects.all()
        elif user.role == 'user':
            # Public posts + their own private posts, test
            posts = Post.objects.filter(
                Q(privacy='public') | Q(author=user)
            )
        else:  # guest
            posts = Post.objects.filter(privacy='public')
            #posts = Post.objects.filter(author=request.user)
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)
        
        

#    def post(self, request):
#        serializer = PostSerializer(data=request.data)
#        if serializer.is_valid():
#            serializer.save()
#            return Response(serializer.data, status=status.HTTP_201_CREATED)
#        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# class CommentListCreate(APIView):
#     permission_classes = [IsAuthenticated]  # ensure only logged-in users can comment

#     def get(self, request):
#         comments = Comment.objects.all()
#         serializer = CommentSerializer(comments, many=True)
#         return Response(serializer.data)

#     def post(self, request):
#         data = request.data.copy()  # make a mutable copy
#         data['user'] = request.user.id  # automatically assign the logged-in user
#         serializer = CommentSerializer(data=data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FeedView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role == 'admin':
            posts = Post.objects.all().order_by('-created_at')
        elif user.role == 'user':
            # Public posts + own private posts
            posts = Post.objects.filter(
                models.Q(privacy='public') | models.Q(author=user)
            ).order_by('-created_at')
        else:  # guest
            posts = Post.objects.filter(privacy='public').order_by('-created_at')
       
        # Setup pagination
        paginator = PageNumberPagination()
        paginator.page_size = 5  # 5 posts per page

        result_page = paginator.paginate_queryset(posts, request)

        # Serialize paginated results
        serializer = PostSerializer(result_page, many=True)

        # Return paginated response
        return paginator.get_paginated_response(serializer.data)


#Delete posts, only admin

# class DeletePostView(APIView):
#     permission_classes = [IsAuthenticated]

#     def delete(self, request, pk):
#         try:
#             post = Post.objects.get(pk=pk)
#         except Post.DoesNotExist:
#             return Response({"error": "Post not found"}, status=404)

#         if request.user.role != 'admin':
#             return Response({"error": "Permission denied"}, status=403)

#         post.delete()
#         return Response({"message": "Post deleted"}, status=204)





#====Comment views======
class PostCommentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

        comments = Comment.objects.filter(post=post)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
class CreatePostCommentView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        data['user'] = request.user.id  # assign logged-in user as author
        data['post'] = post.id  # assign post ID

        serializer = CommentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class DeleteCommentView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def delete(self, request, post_id, comment_id):
        try:
            comment = Comment.objects.get(id=comment_id, post_id=post_id)
        except Comment.DoesNotExist:
            logger.error(f"Comment {comment_id} not found for post {post_id}")
            return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)
        
        comment.delete()
        logger.info(f"Comment {comment_id} deleted by admin '{request.user.username}'")
        return Response({"message": "Comment deleted"}, status=status.HTTP_204_NO_CONTENT) 
#====Likes views


class PostLikeView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        """Allows a user to like a post."""
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            logger.warning(f"User '{request.user.username}' tried to like non-existent post {post_id}")
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if user already liked this post
        existing_like = Like.objects.filter(user=request.user, post=post).first()
        if existing_like:
            logger.info(f"User '{request.user.username}' already liked post {post_id}")
            return Response({"message": "You already liked this post"}, status=status.HTTP_400_BAD_REQUEST)

        # Create like
        like = Like.objects.create(user=request.user, post=post)
        serializer = LikeSerializer(like)
        logger.info(f"User '{request.user.username}' liked post {post_id} (Like ID: {like.id})")
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class PostLikesListView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, post_id):
        """Returns all likes for a specific post."""
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            logger.warning(f"User '{request.user.username}' requested likes for non-existent post {post_id}")
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

        likes = Like.objects.filter(post=post)
        serializer = LikeSerializer(likes, many=True)

        logger.info(f"User '{request.user.username}' viewed likes for post {post_id}")
        return Response(serializer.data, status=status.HTTP_200_OK)
#Feed

class FeedCursorPagination(CursorPagination):
    page_size = 5
    ordering = '-created_at'

class FeedView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # RBAC + privacy filtering
        if user.role == 'admin':
            posts = Post.objects.all()
        elif user.role == 'user':
            # Public posts + user's own private posts
            posts = Post.objects.filter(Q(privacy='public') | Q(author=user))
        else:  # guest
            posts = Post.objects.filter(privacy='public')

        # Order by created_at descending
        posts = posts.order_by('-created_at')

        paginator = FeedCursorPagination()
        result_page = paginator.paginate_queryset(posts, request)

        serializer = PostSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
