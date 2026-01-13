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

from .services import ViteManifestService, UserSyncService
from .models import Post, Comment, Tag, User
from .validators import ValidationService, ValidationError
from .serializers import (
    UserSerializer, UserRegisterSerializer, UserLoginSerializer,
    TagSerializer, CommentSerializer, CommentCreateSerializer,
    PostListSerializer, PostDetailSerializer, PostCreateSerializer, PostUpdateSerializer,
    ErrorSerializer, MessageSerializer,
)

logger = logging.getLogger(__name__)


# ============ 헬퍼 함수 ============

def get_current_user(request: HttpRequest) -> Optional[User]:
    """세션에서 현재 로그인한 사용자를 가져옵니다.

    Args:
        request: HTTP 요청 객체.

    Returns:
        로그인한 사용자 객체 또는 None.
    """
    user_uuid = request.session.get('user_uuid')
    if not user_uuid:
        return None

    try:
        return User.objects.get(uuid=user_uuid)
    except User.DoesNotExist:
        return None


def serialize_post_with_access(post: Post, current_user: Optional[User]) -> dict:
    """게시글을 접근 권한에 따라 직렬화합니다.

    Args:
        post: 직렬화할 게시글.
        current_user: 현재 사용자.

    Returns:
        직렬화된 게시글 데이터.
    """
    can_access = post.can_access(current_user)

    data = {
        'id': post.id,
        'title': post.title if can_access else '비밀글입니다.',
        'content': post.content if can_access else '',
        'author': post.author,
        'user_uuid': str(post.user.uuid) if post.user else None,
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
            author=validated_data.get('author', 'Anonymous'),
            user=current_user,
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

    if not post.can_access(current_user):
        return Response(
            {'error': '이 게시글에 접근할 권한이 없습니다.'},
            status=status.HTTP_403_FORBIDDEN
        )

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

    if not post.can_access(current_user):
        return Response(
            {'error': '이 게시글에 접근할 권한이 없습니다.'},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        ValidationService.validate_json_size(request.body)
        validated_data = ValidationService.validate_post_data(request.data, is_update=True)

        if 'title' in validated_data and validated_data['title']:
            post.title = validated_data['title']
        if 'content' in validated_data and validated_data['content']:
            post.content = validated_data['content']
        if 'author' in validated_data and validated_data['author']:
            post.author = validated_data['author']
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
        return Response({'error': e.message}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"게시글 수정 중 오류 발생: {e}")
        return Response(
            {'error': '요청을 처리하는 중 오류가 발생했습니다.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


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

    if not post.can_access(current_user):
        return Response(
            {'error': '이 게시글에 접근할 권한이 없습니다.'},
            status=status.HTTP_403_FORBIDDEN
        )

    post.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


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

    if not post.can_access(current_user):
        return Response(
            {'error': '이 게시글에 댓글을 작성할 권한이 없습니다.'},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        ValidationService.validate_json_size(request.body)
        validated_data = ValidationService.validate_comment_data(request.data)

        comment = Comment.objects.create(
            post=post,
            content=validated_data['content'],
            author=validated_data['author'],
        )

        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except ValidationError as e:
        logger.warning(f"댓글 생성 검증 실패: {e.message}")
        return Response({'error': e.message}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"댓글 생성 중 오류 발생: {e}")
        return Response(
            {'error': '요청을 처리하는 중 오류가 발생했습니다.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


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


# ============ 인증 API ============

@extend_schema(
    summary='유저 동기화',
    description='WebSocket에서 받은 유저 정보를 세션과 DB에 동기화합니다.',
    request=UserRegisterSerializer,
    responses={
        200: UserSerializer,
        201: UserSerializer,
        400: ErrorSerializer,
    },
    tags=['Auth'],
)
@api_view(['POST'])
def api_user_sync(request: HttpRequest) -> Response:
    """유저 동기화 API.

    WebSocket에서 받은 유저 정보를 세션과 DB에 저장합니다.
    """
    try:
        ValidationService.validate_json_size(request.body)
        validated_data = ValidationService.validate_user_sync_data(request.data)

        user, created = UserSyncService.sync_user(validated_data)
        UserSyncService.save_to_session(request, user)

        serializer = UserSerializer(user)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

    except ValidationError as e:
        logger.warning(f"유저 동기화 검증 실패: {e.message}")
        return Response({'error': e.message}, status=status.HTTP_400_BAD_REQUEST)
    except ValueError as e:
        logger.warning(f"유저 동기화 실패: {e}")
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"유저 동기화 중 오류 발생: {e}")
        return Response(
            {'error': '요청을 처리하는 중 오류가 발생했습니다.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    summary='회원가입',
    description='새로운 사용자를 등록합니다.',
    request=UserRegisterSerializer,
    responses={
        201: UserSerializer,
        400: ErrorSerializer,
        409: ErrorSerializer,
    },
    tags=['Auth'],
)
@api_view(['POST'])
def api_register(request: HttpRequest) -> Response:
    """회원가입 API."""
    try:
        ValidationService.validate_json_size(request.body)
        validated_data = ValidationService.validate_register_data(request.data)

        if User.objects.filter(username=validated_data['username']).exists():
            return Response(
                {'error': '이미 사용 중인 사용자명입니다.'},
                status=status.HTTP_409_CONFLICT
            )

        user = User(username=validated_data['username'])
        user.set_password(validated_data['password'])
        user.save()

        logger.info(f"새 사용자 등록: {user.username}")
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except ValidationError as e:
        logger.warning(f"회원가입 검증 실패: {e.message}")
        return Response({'error': e.message}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"회원가입 중 오류 발생: {e}")
        return Response(
            {'error': '요청을 처리하는 중 오류가 발생했습니다.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    summary='로그인',
    description='사용자 인증을 수행하고 세션을 생성합니다.',
    request=UserLoginSerializer,
    responses={
        200: UserSerializer,
        400: ErrorSerializer,
        401: ErrorSerializer,
    },
    tags=['Auth'],
)
@api_view(['POST'])
def api_login(request: HttpRequest) -> Response:
    """로그인 API."""
    try:
        ValidationService.validate_json_size(request.body)
        validated_data = ValidationService.validate_login_data(request.data)

        try:
            user = User.objects.get(username=validated_data['username'])
        except User.DoesNotExist:
            return Response(
                {'error': '사용자명 또는 비밀번호가 올바르지 않습니다.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.check_password(validated_data['password']):
            return Response(
                {'error': '사용자명 또는 비밀번호가 올바르지 않습니다.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        request.session['user_uuid'] = str(user.uuid)
        request.session['username'] = user.username
        request.session['is_admin'] = user.is_admin

        logger.info(f"사용자 로그인: {user.username}")
        serializer = UserSerializer(user)
        return Response(serializer.data)

    except ValidationError as e:
        logger.warning(f"로그인 검증 실패: {e.message}")
        return Response({'error': e.message}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"로그인 중 오류 발생: {e}")
        return Response(
            {'error': '요청을 처리하는 중 오류가 발생했습니다.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    summary='로그아웃',
    description='현재 세션을 종료합니다.',
    responses={
        200: MessageSerializer,
    },
    tags=['Auth'],
)
@api_view(['POST'])
def api_logout(request: HttpRequest) -> Response:
    """로그아웃 API."""
    username = request.session.get('username', 'Unknown')
    request.session.flush()
    logger.info(f"사용자 로그아웃: {username}")
    return Response({'message': '로그아웃되었습니다.'})


@extend_schema(
    summary='현재 사용자 정보',
    description='현재 로그인한 사용자의 정보를 조회합니다.',
    responses={
        200: UserSerializer,
        401: ErrorSerializer,
    },
    tags=['Auth'],
)
@api_view(['GET'])
def api_me(request: HttpRequest) -> Response:
    """현재 사용자 정보 조회 API."""
    current_user = get_current_user(request)

    if not current_user:
        return Response(
            {'error': '로그인이 필요합니다.'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    serializer = UserSerializer(current_user)
    return Response(serializer.data)
