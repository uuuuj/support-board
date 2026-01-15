"""Support Board API Views.

Django REST Framework를 사용한 API 뷰 모듈입니다.
게시글, 댓글, 사용자 인증 기능을 제공합니다.
"""

import logging
from typing import Optional

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.db.models import Q

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from .services import ViteManifestService
from .models import Post, Comment, Tag
from .validators import ValidationService, ValidationError
from .serializers import (
    TagSerializer, CommentSerializer, CommentCreateSerializer,
    PostListSerializer, PostDetailSerializer, PostCreateSerializer, PostUpdateSerializer,
    ErrorSerializer, MessageSerializer,
)

logger = logging.getLogger(__name__)


# ============ 헬퍼 함수 ============

def get_current_user(request: HttpRequest) -> Optional[dict]:
    """세션에서 현재 로그인한 사용자 정보를 가져옵니다.

    Args:
        request: HTTP 요청 객체.

    Returns:
        로그인한 사용자 정보 dict 또는 None.
    """
    user_id = request.session.get('user_id')
    if not user_id:
        return None

    return {
        'user_id': user_id,
        'user_name': request.session.get('user_name'),
        'user_compname': request.session.get('user_compname'),
        'user_deptname': request.session.get('user_deptname'),
        'is_admin': request.session.get('is_admin', False),
    }


def serialize_post_with_access(post: Post, current_user: Optional[dict]) -> dict:
    """게시글을 접근 권한에 따라 직렬화합니다.

    Args:
        post: 직렬화할 게시글.
        current_user: 현재 사용자 정보 dict.

    Returns:
        직렬화된 게시글 데이터.
    """
    user_id = current_user.get('user_id') if current_user else None
    is_admin = current_user.get('is_admin', False) if current_user else False
    can_access = post.can_access(user_id, is_admin)

    data = {
        'id': post.id,
        'title': post.title if can_access else '비밀글입니다.',
        'content': post.content if can_access else '',
        'user_name': post.user_name,
        'user_id': post.user_id,
        'user_compname': post.user_compname if can_access else None,
        'user_deptname': post.user_deptname if can_access else None,
        'tags': [tag.name for tag in post.tags.all()] if can_access else [],
        'is_resolved': post.is_resolved,
        'is_private': post.is_private,
        'comments_count': post.comments.count(),
        'created_at': post.created_at.isoformat(),
        'updated_at': post.updated_at.isoformat(),
    }
    return data


# ============ 프론트엔드 뷰 ============

def index(request: HttpRequest) -> HttpResponse:
    """React SPA를 서빙하는 뷰.

    Args:
        request: HTTP 요청 객체.

    Returns:
        HttpResponse: 렌더링된 index.html 템플릿.
    """
    manifest_service = ViteManifestService()
    entry = manifest_service.get_entry()

    context = {
        'js_file': entry.js_file,
        'css_file': entry.css_file,
    }
    return render(request, 'support_board/index.html', context)


# ============ 게시글 API ============

@extend_schema(
    summary='게시글 목록 조회',
    description='게시글 목록을 조회합니다. 검색 및 필터링을 지원합니다.',
    parameters=[
        OpenApiParameter(name='q', description='통합 검색어 (제목, 내용, 작성자, 태그)', type=str),
        OpenApiParameter(name='title', description='제목 검색', type=str),
        OpenApiParameter(name='content', description='내용 검색', type=str),
        OpenApiParameter(name='author', description='작성자 검색', type=str),
        OpenApiParameter(name='tag', description='태그 검색', type=str),
        OpenApiParameter(name='is_resolved', description='해결 여부 필터', type=bool),
    ],
    responses={
        200: OpenApiResponse(description='게시글 목록'),
    },
    tags=['Posts'],
)
@api_view(['GET'])
def api_posts_list(request: HttpRequest) -> Response:
    """게시글 목록 조회 API."""
    current_user = get_current_user(request)

    # 검색 파라미터
    q = request.GET.get('q', '')
    title = request.GET.get('title', '')
    content = request.GET.get('content', '')
    author = request.GET.get('author', '')
    tag = request.GET.get('tag', '')
    is_resolved = request.GET.get('is_resolved', '')

    posts = Post.objects.all()

    # 통합 검색
    if q:
        posts = posts.filter(
            Q(title__icontains=q) |
            Q(content__icontains=q) |
            Q(author__icontains=q) |
            Q(tags__name__icontains=q)
        ).distinct()

    # 개별 필터
    if title:
        posts = posts.filter(title__icontains=title)
    if content:
        posts = posts.filter(content__icontains=content)
    if author:
        posts = posts.filter(author__icontains=author)
    if tag:
        posts = posts.filter(tags__name__icontains=tag)
    if is_resolved:
        posts = posts.filter(is_resolved=(is_resolved.lower() == 'true'))

    # 비밀글 접근 권한에 따라 직렬화
    serialized_posts = [
        serialize_post_with_access(post, current_user)
        for post in posts
    ]

    return Response({
        'posts': serialized_posts,
        'count': len(serialized_posts),
    })


@extend_schema(
    summary='게시글 생성',
    description='새로운 게시글을 생성합니다. 비밀글 작성 시 로그인이 필요합니다.',
    request=PostCreateSerializer,
    responses={
        201: PostListSerializer,
        400: ErrorSerializer,
        401: ErrorSerializer,
    },
    tags=['Posts'],
)
@api_view(['POST'])
def api_posts_create(request: HttpRequest) -> Response:
    """게시글 생성 API."""
    current_user = get_current_user(request)

    try:
        ValidationService.validate_json_size(request.body)
        validated_data = ValidationService.validate_post_data(request.data)

        # 비밀글 작성 시 로그인 필수
        is_private = validated_data.get('is_private', False)
        if is_private and not current_user:
            return Response(
                {'error': '비밀글을 작성하려면 로그인이 필요합니다.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        post = Post.objects.create(
            title=validated_data.get('title', ''),
            content=validated_data.get('content', ''),
            user_name=validated_data.get('user_name', 'Anonymous'),
            user_id=current_user.get('user_id') if current_user else None,
            user_compname=current_user.get('user_compname') if current_user else None,
            user_deptname=current_user.get('user_deptname') if current_user else None,
            is_resolved=validated_data.get('is_resolved', False),
            is_private=is_private,
        )

        # 태그 처리
        for tag_name in validated_data.get('tags', []):
            tag_obj, _ = Tag.objects.get_or_create(name=tag_name)
            post.tags.add(tag_obj)

        serializer = PostListSerializer(post)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except ValidationError as e:
        logger.warning(f"게시글 생성 검증 실패: {e.message}")
        return Response({'error': e.message}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"게시글 생성 중 오류 발생: {e}")
        return Response(
            {'error': '요청을 처리하는 중 오류가 발생했습니다.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    summary='게시글 상세 조회',
    description='게시글 상세 정보와 댓글을 조회합니다. 비밀글은 작성자 또는 관리자만 조회 가능합니다.',
    responses={
        200: PostDetailSerializer,
        403: ErrorSerializer,
        404: ErrorSerializer,
    },
    tags=['Posts'],
)
@api_view(['GET'])
def api_post_detail(request: HttpRequest, post_id: int) -> Response:
    """게시글 상세 조회 API."""
    post = get_object_or_404(Post, id=post_id)
    current_user = get_current_user(request)

    user_id = current_user.get('user_id') if current_user else None
    is_admin = current_user.get('is_admin', False) if current_user else False

    if not post.can_access(user_id, is_admin):
        logger.warning(f"게시글 접근 거부: post_id={post_id}, user_id={user_id}")
        return Response({
            'access_denied': True,
            'message': '이 게시글에 접근할 권한이 없습니다.',
        })

    serializer = PostDetailSerializer(post)
    return Response(serializer.data)


@extend_schema(
    summary='게시글 수정',
    description='게시글을 수정합니다.',
    request=PostUpdateSerializer,
    responses={
        200: PostListSerializer,
        400: ErrorSerializer,
        403: ErrorSerializer,
        404: ErrorSerializer,
    },
    tags=['Posts'],
)
@api_view(['PUT'])
def api_post_update(request: HttpRequest, post_id: int) -> Response:
    """게시글 수정 API."""
    post = get_object_or_404(Post, id=post_id)
    current_user = get_current_user(request)

    user_id = current_user.get('user_id') if current_user else None
    is_admin = current_user.get('is_admin', False) if current_user else False

    if not post.can_access(user_id, is_admin):
        logger.warning(f"게시글 수정 권한 거부: post_id={post_id}, user_id={user_id}")
        return Response({
            'access_denied': True,
            'message': '이 게시글을 수정할 권한이 없습니다.',
        })

    try:
        ValidationService.validate_json_size(request.body)
        validated_data = ValidationService.validate_post_data(request.data, is_update=True)

        if 'title' in validated_data and validated_data['title']:
            post.title = validated_data['title']
        if 'content' in validated_data and validated_data['content']:
            post.content = validated_data['content']
        if 'user_name' in validated_data and validated_data['user_name']:
            post.user_name = validated_data['user_name']
        if 'is_resolved' in validated_data:
            post.is_resolved = validated_data['is_resolved']
        if 'is_private' in validated_data:
            post.is_private = validated_data['is_private']

        post.save()

        if 'tags' in validated_data:
            post.tags.clear()
            for tag_name in validated_data['tags']:
                tag_obj, _ = Tag.objects.get_or_create(name=tag_name)
                post.tags.add(tag_obj)

        serializer = PostListSerializer(post)
        return Response(serializer.data)

    except ValidationError as e:
        logger.warning(f"게시글 수정 검증 실패: {e.message}")
        return Response({
            'access_denied': True,
            'message': e.message,
        })
    except Exception as e:
        logger.error(f"게시글 수정 중 오류 발생: {e}")
        return Response({
            'access_denied': True,
            'message': '요청을 처리하는 중 오류가 발생했습니다.',
        })


@extend_schema(
    summary='게시글 삭제',
    description='게시글을 삭제합니다.',
    responses={
        204: None,
        403: ErrorSerializer,
        404: ErrorSerializer,
    },
    tags=['Posts'],
)
@api_view(['DELETE'])
def api_post_delete(request: HttpRequest, post_id: int) -> Response:
    """게시글 삭제 API."""
    post = get_object_or_404(Post, id=post_id)
    current_user = get_current_user(request)

    user_id = current_user.get('user_id') if current_user else None
    is_admin = current_user.get('is_admin', False) if current_user else False

    if not post.can_access(user_id, is_admin):
        logger.warning(f"게시글 삭제 권한 거부: post_id={post_id}, user_id={user_id}")
        return Response({
            'access_denied': True,
            'message': '이 게시글을 삭제할 권한이 없습니다.',
        })

    post.delete()
    return Response({'success': True, 'message': '게시글이 삭제되었습니다.'})


# ============ 댓글 API ============

@extend_schema(
    summary='댓글 생성',
    description='게시글에 댓글을 작성합니다. 비밀글에는 작성자 또는 관리자만 댓글 작성 가능합니다.',
    request=CommentCreateSerializer,
    responses={
        201: CommentSerializer,
        400: ErrorSerializer,
        403: ErrorSerializer,
        404: ErrorSerializer,
    },
    tags=['Comments'],
)
@api_view(['POST'])
def api_post_comments(request: HttpRequest, post_id: int) -> Response:
    """댓글 생성 API."""
    post = get_object_or_404(Post, id=post_id)
    current_user = get_current_user(request)

    user_id = current_user.get('user_id') if current_user else None
    is_admin = current_user.get('is_admin', False) if current_user else False

    if not post.can_access(user_id, is_admin):
        logger.warning(f"댓글 작성 권한 거부: post_id={post_id}, user_id={user_id}")
        return Response({
            'access_denied': True,
            'message': '이 게시글에 댓글을 작성할 권한이 없습니다.',
        })

    try:
        ValidationService.validate_json_size(request.body)
        validated_data = ValidationService.validate_comment_data(request.data)

        comment = Comment.objects.create(
            post=post,
            content=validated_data['content'],
            user_name=validated_data.get('user_name', 'Anonymous'),
            user_id=current_user.get('user_id') if current_user else None,
            user_compname=current_user.get('user_compname') if current_user else None,
            user_deptname=current_user.get('user_deptname') if current_user else None,
        )

        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except ValidationError as e:
        logger.warning(f"댓글 생성 검증 실패: {e.message}")
        return Response({
            'access_denied': True,
            'message': e.message,
        })
    except Exception as e:
        logger.error(f"댓글 생성 중 오류 발생: {e}")
        return Response({
            'access_denied': True,
            'message': '요청을 처리하는 중 오류가 발생했습니다.',
        })


# ============ 태그 API ============

@extend_schema(
    summary='태그 목록 조회',
    description='모든 태그 목록을 조회합니다.',
    responses={
        200: TagSerializer(many=True),
    },
    tags=['Tags'],
)
@api_view(['GET'])
def api_tags(request: HttpRequest) -> Response:
    """태그 목록 조회 API."""
    tags = Tag.objects.all()
    return Response({
        'tags': [{'id': tag.id, 'name': tag.name} for tag in tags]
    })


