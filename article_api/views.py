import os, re

import google.generativeai as genai
from jsonschema import ValidationError
import requests
from dotenv import load_dotenv
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Article, Tag, User
from .serializers import (
    ArticleCreateSerializer,
    ArticleDeleteTagSerializer,
    ArticleSerializer,
    UserSerializer,
    WikipediaSearchSerializer,
)

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class RegisterUserView(APIView):
    """Register user"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user: User = serializer.save()
            user.set_password(request.data["password"])
            user.save()
            return Response(
                {"message": "User registered successfully"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ArticleViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    def list(self, request):
        try:
            user = request.user
            articles = Article.objects.filter(user=user).all()
            serializer = ArticleSerializer(articles, many=True)
            return Response(serializer.data, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    def create(self, request):
        user = request.user
        serializer = ArticleCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        title = serializer.validated_data["title"]
        snippet = serializer.validated_data["snippet"]
        tags = []
        try:
            if not tags:
                model = genai.GenerativeModel("gemini-1.5-flash")
                prompt = f"Generate relevant tags for a wikipedia article titled '{title}' with snippet '{snippet}'. Your output should only contain tags separated by comma and no extra space."
                response = model.generate_content(prompt)
                tags = [tag.strip() for tag in response.text.split(",") if tag.strip()]
        except Exception as e:
            return Response(
                {"error": f"Failed to generate tags: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        tag_objects = self._get_or_create_tags(tags)
        article = Article.objects.create(user=user, title=title, snippet=snippet)
        article.tags.set(tag_objects)
        return Response(ArticleSerializer(article).data, status=status.HTTP_201_CREATED)

    def _get_or_create_tags(self, tags):
        tag_objects = []
        for tag_name in tags:
            tag, _ = Tag.objects.get_or_create(name=tag_name.strip())
            tag_objects.append(tag)
        return tag_objects
    def delete(self, request, pk):
        try:
            article = Article.objects.get(pk=pk)
            article.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Article.DoesNotExist:
            return Response({"error": "Article not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=["delete"])
    def delete_tag(self, request, pk):
        try:
            serializer = ArticleDeleteTagSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            article = Article.objects.get(pk=pk)
            tag_object = Tag.objects.get(name=serializer.validated_data["name"])
            
            if tag_object:
                article.tags.remove(tag_object)
            
            return Response(ArticleSerializer(article).data, status=status.HTTP_200_OK)
        except Article.DoesNotExist:
            return Response({"error": "Article not found."}, status=status.HTTP_404_NOT_FOUND)
        except Tag.DoesNotExist:
            return Response({"error": "Tag not found."}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=["post"])
    def add_tag(self, request, pk):
        try:
            article = Article.objects.get(pk=pk)
            tag_object, _ = Tag.objects.get_or_create(name=request.data.get("name"))
            article.tags.add(tag_object)
            return Response(ArticleSerializer(article).data, status=status.HTTP_201_CREATED)
        except Article.DoesNotExist:
            return Response({"error": "Article not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=["post"])
    def search(self, request):
        try:
            # Validate input
            serializer = WikipediaSearchSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            query = serializer.validated_data["query"]

            # Wikipedia API request
            response = requests.get(
                "https://en.wikipedia.org/w/api.php",
                params={
                    "action": "query",
                    "list": "search",
                    "srsearch": query,
                    "format": "json",
                },
            )
            response.raise_for_status()
            
            data = response.json().get("query", {}).get("search", [])
            cleaned_data = [
                {
                    **entry,
                    "snippet": re.sub(r"</?span.*?>", "", entry.get("snippet", "")).replace("&quot;", "")
                }
                for entry in data
            ]
            return Response(cleaned_data, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except requests.RequestException as e:
            return Response(
                {"error": f"An error occurred while connecting to Wikipedia: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
