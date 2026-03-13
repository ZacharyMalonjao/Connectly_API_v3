
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


# Create your models here.


# class User(models.Model):
#     username = models.CharField(max_length=100, unique=True)  # User's unique username
#     email = models.EmailField(unique=True)  # User's unique email
#     created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the user was created

#     def __str__(self):
#         return self.username

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User'),
        ('guest', 'Guest'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    def __str__(self):
        return f"{self.username} ({self.role})"


class Post(models.Model):
    content = models.TextField()  # The text content of the post
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='posts', on_delete=models.CASCADE)  # The user who created the post
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the post was created
    title = models.CharField(max_length=255, default='Untitled')
    POST_TYPES = (
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
    )
    post_type = models.CharField(max_length=10, choices=POST_TYPES, default='text')
    metadata = models.JSONField(default=dict, blank=True) 
    PRIVACY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]
    privacy = models.CharField(max_length=10, choices=PRIVACY_CHOICES, default='public')

    def __str__(self):
        return f"{self.author.username}: {self.content[:30]} ({self.privacy})" # Return first 50 characters of the post
    
class Comment(models.Model):
    content = models.TextField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='comments',
        on_delete=models.CASCADE
)
    post = models.ForeignKey(
        Post,
        related_name='comments',
        on_delete=models.CASCADE
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    
    def __str__(self):
     return f"Comment by {self.user.username} on Post {self.post.id}"

class Like(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='likes',
        on_delete=models.CASCADE
    )
    post = models.ForeignKey(
        Post,
        related_name='likes',
        on_delete=models.CASCADE
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')  # Prevents a user from liking the same post multiple times

    def __str__(self):
        return f"{self.user.username} liked Post {self.post.id}"