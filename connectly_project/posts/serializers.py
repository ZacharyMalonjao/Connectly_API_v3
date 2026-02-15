from rest_framework import serializers
from .models import Post, Comment
from django.contrib.auth.models import User
from singletons.logger_singleton import LoggerSingleton
from .models import Like

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    
class PostSerializer(serializers.ModelSerializer):
    comments = serializers.StringRelatedField(
        many=True,
        read_only=True
    )

    class Meta:
        model = Post
        fields = ['id', 'content', 'author', 'created_at', 'comments']
        read_only_fields = ['author'] 
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'content', 'user', 'post', 'timestamp']

    def validate_post(self, value):
        if not Post.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Post not found.")
        return value

    def validate_user(self, value):
        if not User.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("User not found.")
        return value
    

logger = LoggerSingleton().get_logger()

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'timestamp']

    def validate_post(self, value):
        if not Post.objects.filter(id=value.id).exists():
            logger.warning(f"Like validation failed: Post {value.id} not found")
            raise serializers.ValidationError("Post not found.")
        return value

    def validate_user(self, value):
        if not User.objects.filter(id=value.id).exists():
            logger.warning(f"Like validation failed: User {value.id} not found")
            raise serializers.ValidationError("User not found.")
        return value

    def create(self, validated_data):
        like = super().create(validated_data)
        logger.info(f"Like created: User {like.user.id} liked Post {like.post.id}")
        return like
