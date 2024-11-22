from rest_framework import serializers
from .models import Article, User

class ArticleSerializer(serializers.ModelSerializer):
    tags = serializers.StringRelatedField(many=True)
    class Meta:
        model = Article
        fields = ["id", "title", "snippet", "tags"]

class ArticleCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    snippet = serializers.CharField(max_length=10000)

class ArticleDeleteTagSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=300)

class ArticleAddTagSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=300)

class WikipediaSearchSerializer(serializers.Serializer):
    query = serializers.CharField(max_length=255, required=True)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]
