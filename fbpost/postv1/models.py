from django.db import models
import datetime


# Create your models here.


class User(models.Model):
    name = models.CharField(max_length=50)

    profile_pic_url = models.URLField(max_length=200)


class Post(models.Model):
    posted_at = models.DateTimeField(auto_now_add=True)

    content = models.TextField()

    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')


class Comment(models.Model):
    content = models.TextField()
    commented_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    commented_at = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE, null=True, default=None)

    # considering replies also as a comment
    parent_comment = models.ForeignKey('self', related_name="replies", on_delete=models.CASCADE, null=True,
                                       default=None)


class Reaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reactions')
    reaction = models.CharField(max_length=15)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reactions', null=True, default=None)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="reactions", null=True, default=None)
