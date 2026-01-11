from django.urls import path
from . import views

app_name = 'support_board'

urlpatterns = [
    path('', views.index, name='index'),

    # API endpoints
    path('api/posts/', views.api_posts, name='api_posts'),
    path('api/posts/<int:post_id>/', views.api_post_detail, name='api_post_detail'),
    path('api/posts/<int:post_id>/comments/', views.api_post_comments, name='api_post_comments'),
    path('api/tags/', views.api_tags, name='api_tags'),
]
