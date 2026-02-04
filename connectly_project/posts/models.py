from django.db import models
from django.db import models
from django.contrib.auth.models import User 

# Create your models here.


#class User(models.Model):
#    username = models.CharField(max_length=100, unique=True)  # User's unique username
#    email = models.EmailField(unique=True)  # User's unique email
#    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the user was created

#    def __str__(self):
#        return self.username


class Post(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:50]  # Return first 50 characters of the post

class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Comment by {self.author.username} on Post {self.post.id}"

