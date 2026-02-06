#from django.utils.decorators import method_decorator
#from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from .permissions import IsPostAuthor
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Post, Comment
from .serializers import UserSerializer, PostSerializer, CommentSerializer
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from posts.factories.post_factory import PostFactory
from singletons.logger_singleton import LoggerSingleton

logger = LoggerSingleton().get_logger()


#METHOD INDEX
#1. UserListCreate
#2. PostListCreate
#3. CommentsListCreate
#4. Login
#5. PostDetailView
#6. ProtectedView

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
#@method_decorator(ensure_csrf_cookie, name='dispatch')   
class PostListCreate(APIView):
    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

#    def post(self, request):
#        serializer = PostSerializer(data=request.data)
#        if serializer.is_valid():
#            serializer.save()
#            return Response(serializer.data, status=status.HTTP_201_CREATED)
#        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentListCreate(APIView):
    def get(self, request):
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login

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

class PostDetailView(APIView):
    permission_classes = [IsAuthenticated, IsPostAuthor]

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
        return Response({"id": post.id, "content": post.content, "author": post.author.username})
    
class ProtectedView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": f"Authenticated as {request.user.username}!"})