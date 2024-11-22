from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=300)

    def __str__(self):
        return self.name


class Article(models.Model):
    """Model for storing saved articles."""

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    snippet = models.TextField()
    tags = models.ManyToManyField(Tag, related_name="article")

    def __str__(self):
        return self.title
