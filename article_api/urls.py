from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ArticleViewSet, RegisterUserView

article_router = DefaultRouter()
article_router.register(r"", ArticleViewSet, basename="article")

urlpatterns = [
    path("", include(article_router.urls)),
    path("api/register/", RegisterUserView.as_view(), name="register-user"),
]
