import json
import logging
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.db.models import Q

from .services import ViteManifestService
from .models import Post, Comment, Tag
from .validators import ValidationService, ValidationError

logger = logging.getLogger(__name__)


def index(request: HttpRequest) -> HttpResponse:
    """React SPA를 서빙하는 뷰.

    Vite manifest를 파싱하여 빌드된 JS/CSS 파일 경로를 템플릿에 전달합니다.
    manifest가 없는 경우(개발 모드) React dev server를 사용합니다.

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


# ============ API Views ============

def serialize_post(post):
    """Post 객체를 딕셔너리로 직렬화"""
    return {
        'id': post.id,
        'title': post.title,
        'content': post.content,
        'author': post.author,
        'tags': [tag.name for tag in post.tags.all()],
        'is_resolved': post.is_resolved,
        'comments_count': post.comments.count(),
        'created_at': post.created_at.isoformat(),
        'updated_at': post.updated_at.isoformat(),
    }


def serialize_comment(comment):
    """Comment 객체를 딕셔너리로 직렬화"""
    return {
        'id': comment.id,
        'content': comment.content,
        'author': comment.author,
        'created_at': comment.created_at.isoformat(),
        'updated_at': comment.updated_at.isoformat(),
    }


@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_posts(request: HttpRequest) -> JsonResponse:
    """게시글 목록 조회 및 생성 API.

    Endpoint:
        GET /api/posts/ - 게시글 목록 조회
        POST /api/posts/ - 새 게시글 생성

    Request Body (POST):
        - title (str): 게시글 제목 (필수, 최대 200자)
        - content (str): 게시글 내용 (필수, 최대 10000자)
        - author (str): 작성자 (선택, 기본값: Anonymous, 최대 50자)
        - tags (list): 태그 목록 (선택, 최대 10개)
        - is_resolved (bool): 해결 여부 (선택, 기본값: False)

    Response:
        200 OK: 게시글 목록 반환
        201 Created: 게시글 생성 성공
        400 Bad Request: 유효하지 않은 요청 데이터

    Args:
        request: HTTP 요청 객체.

    Returns:
        JsonResponse: 게시글 목록 또는 생성된 게시글 정보.
    """
    if request.method == "GET":
        # 검색 파라미터
        q = request.GET.get('q', '')  # 통합 검색어
        title = request.GET.get('title', '')
        content = request.GET.get('content', '')
        author = request.GET.get('author', '')
        tag = request.GET.get('tag', '')
        is_resolved = request.GET.get('is_resolved', '')

        posts = Post.objects.all()

        # 통합 검색 (제목, 내용, 작성자에서 검색)
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

        return JsonResponse({
            'posts': [serialize_post(post) for post in posts],
            'count': posts.count(),
        })

    elif request.method == "POST":
        try:
            # JSON 크기 검증
            ValidationService.validate_json_size(request.body)
            data = json.loads(request.body)

            # 입력값 검증 및 sanitization
            validated_data = ValidationService.validate_post_data(data)

            post = Post.objects.create(
                title=validated_data.get('title', ''),
                content=validated_data.get('content', ''),
                author=validated_data.get('author', 'Anonymous'),
                is_resolved=validated_data.get('is_resolved', False),
            )

            # 태그 처리 (이미 sanitize됨)
            for tag_name in validated_data.get('tags', []):
                tag_obj, _ = Tag.objects.get_or_create(name=tag_name)
                post.tags.add(tag_obj)

            return JsonResponse(serialize_post(post), status=201)

        except ValidationError as e:
            logger.warning(f"게시글 생성 검증 실패: {e.message}")
            return JsonResponse({'error': e.message}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': '올바른 JSON 형식이 아닙니다.'}, status=400)
        except Exception as e:
            logger.error(f"게시글 생성 중 오류 발생: {e}")
            return JsonResponse({'error': '요청을 처리하는 중 오류가 발생했습니다.'}, status=500)


@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def api_post_detail(request: HttpRequest, post_id: int) -> JsonResponse:
    """게시글 상세 조회, 수정, 삭제 API.

    Endpoint:
        GET /api/posts/<post_id>/ - 게시글 상세 조회
        PUT /api/posts/<post_id>/ - 게시글 수정
        DELETE /api/posts/<post_id>/ - 게시글 삭제

    Request Body (PUT):
        - title (str): 게시글 제목 (선택, 최대 200자)
        - content (str): 게시글 내용 (선택, 최대 10000자)
        - author (str): 작성자 (선택, 최대 50자)
        - tags (list): 태그 목록 (선택, 최대 10개)
        - is_resolved (bool): 해결 여부 (선택)

    Response:
        200 OK: 게시글 정보 반환
        204 No Content: 게시글 삭제 성공
        400 Bad Request: 유효하지 않은 요청 데이터
        404 Not Found: 게시글 없음

    Args:
        request: HTTP 요청 객체.
        post_id: 게시글 ID.

    Returns:
        JsonResponse: 게시글 정보 또는 상태 메시지.
    """
    post = get_object_or_404(Post, id=post_id)

    if request.method == "GET":
        data = serialize_post(post)
        data['comments'] = [serialize_comment(c) for c in post.comments.all()]
        return JsonResponse(data)

    elif request.method == "PUT":
        try:
            # JSON 크기 검증
            ValidationService.validate_json_size(request.body)
            data = json.loads(request.body)

            # 입력값 검증 및 sanitization (수정 모드)
            validated_data = ValidationService.validate_post_data(data, is_update=True)

            # 검증된 데이터만 업데이트
            if 'title' in validated_data and validated_data['title']:
                post.title = validated_data['title']
            if 'content' in validated_data and validated_data['content']:
                post.content = validated_data['content']
            if 'author' in validated_data and validated_data['author']:
                post.author = validated_data['author']
            if 'is_resolved' in validated_data:
                post.is_resolved = validated_data['is_resolved']

            post.save()

            # 태그 업데이트 (이미 sanitize됨)
            if 'tags' in validated_data:
                post.tags.clear()
                for tag_name in validated_data['tags']:
                    tag_obj, _ = Tag.objects.get_or_create(name=tag_name)
                    post.tags.add(tag_obj)

            return JsonResponse(serialize_post(post))

        except ValidationError as e:
            logger.warning(f"게시글 수정 검증 실패: {e.message}")
            return JsonResponse({'error': e.message}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': '올바른 JSON 형식이 아닙니다.'}, status=400)
        except Exception as e:
            logger.error(f"게시글 수정 중 오류 발생: {e}")
            return JsonResponse({'error': '요청을 처리하는 중 오류가 발생했습니다.'}, status=500)

    elif request.method == "DELETE":
        post.delete()
        return JsonResponse({'message': 'Post deleted'}, status=204)


@csrf_exempt
@require_http_methods(["POST"])
def api_post_comments(request: HttpRequest, post_id: int) -> JsonResponse:
    """댓글 생성 API.

    Endpoint:
        POST /api/posts/<post_id>/comments/ - 댓글 생성

    Request Body:
        - content (str): 댓글 내용 (필수, 최대 10000자)
        - author (str): 작성자 (선택, 기본값: Anonymous, 최대 50자)

    Response:
        201 Created: 댓글 생성 성공
        400 Bad Request: 유효하지 않은 요청 데이터
        404 Not Found: 게시글 없음

    Args:
        request: HTTP 요청 객체.
        post_id: 게시글 ID.

    Returns:
        JsonResponse: 생성된 댓글 정보.
    """
    post = get_object_or_404(Post, id=post_id)

    try:
        # JSON 크기 검증
        ValidationService.validate_json_size(request.body)
        data = json.loads(request.body)

        # 입력값 검증 및 sanitization
        validated_data = ValidationService.validate_comment_data(data)

        comment = Comment.objects.create(
            post=post,
            content=validated_data['content'],
            author=validated_data['author'],
        )
        return JsonResponse(serialize_comment(comment), status=201)

    except ValidationError as e:
        logger.warning(f"댓글 생성 검증 실패: {e.message}")
        return JsonResponse({'error': e.message}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'error': '올바른 JSON 형식이 아닙니다.'}, status=400)
    except Exception as e:
        logger.error(f"댓글 생성 중 오류 발생: {e}")
        return JsonResponse({'error': '요청을 처리하는 중 오류가 발생했습니다.'}, status=500)


@require_http_methods(["GET"])
def api_tags(request):
    """태그 목록 조회"""
    tags = Tag.objects.all()
    return JsonResponse({
        'tags': [{'id': tag.id, 'name': tag.name} for tag in tags]
    })
