from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from . import views

app_name = 'support_board'

urlpatterns = [
    # 프론트엔드
    path('', views.index, name='index'),

    # API - Posts
    path('api/posts/', views.api_posts_list, name='api_posts_list'),
    path('api/posts/create/', views.api_posts_create, name='api_posts_create'),
    path('api/posts/<int:post_id>/', views.api_post_detail, name='api_post_detail'),
    path('api/posts/<int:post_id>/update/', views.api_post_update, name='api_post_update'),
    path('api/posts/<int:post_id>/delete/', views.api_post_delete, name='api_post_delete'),
    path('api/posts/<int:post_id>/comments/', views.api_post_comments, name='api_post_comments'),

    # API - Tags
    path('api/tags/', views.api_tags, name='api_tags'),

    # API - Auth
    path('api/users/sync/', views.api_user_sync, name='api_user_sync'),
    path('api/users/register/', views.api_register, name='api_register'),
    path('api/users/login/', views.api_login, name='api_login'),
    path('api/users/logout/', views.api_logout, name='api_logout'),
    path('api/users/me/', views.api_me, name='api_me'),

    # Swagger / OpenAPI
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='support_board:schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='support_board:schema'), name='redoc'),
]
