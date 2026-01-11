import json
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

from .services import ViteManifestService
from .models import Post, Comment, Tag


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
def api_posts(request):
    """게시글 목록 조회 및 생성"""
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
            data = json.loads(request.body)
            post = Post.objects.create(
                title=data.get('title', ''),
                content=data.get('content', ''),
                author=data.get('author', 'Anonymous'),
                is_resolved=data.get('is_resolved', False),
            )
            # 태그 처리
            tag_names = data.get('tags', [])
            for tag_name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=tag_name.strip())
                post.tags.add(tag)

            return JsonResponse(serialize_post(post), status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def api_post_detail(request, post_id):
    """게시글 상세 조회, 수정, 삭제"""
    post = get_object_or_404(Post, id=post_id)

    if request.method == "GET":
        data = serialize_post(post)
        data['comments'] = [serialize_comment(c) for c in post.comments.all()]
        return JsonResponse(data)

    elif request.method == "PUT":
        try:
            data = json.loads(request.body)
            post.title = data.get('title', post.title)
            post.content = data.get('content', post.content)
            post.author = data.get('author', post.author)
            post.is_resolved = data.get('is_resolved', post.is_resolved)
            post.save()

            # 태그 업데이트
            if 'tags' in data:
                post.tags.clear()
                for tag_name in data['tags']:
                    tag, _ = Tag.objects.get_or_create(name=tag_name.strip())
                    post.tags.add(tag)

            return JsonResponse(serialize_post(post))
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    elif request.method == "DELETE":
        post.delete()
        return JsonResponse({'message': 'Post deleted'}, status=204)


@csrf_exempt
@require_http_methods(["POST"])
def api_post_comments(request, post_id):
    """댓글 생성"""
    post = get_object_or_404(Post, id=post_id)

    try:
        data = json.loads(request.body)
        comment = Comment.objects.create(
            post=post,
            content=data.get('content', ''),
            author=data.get('author', 'Anonymous'),
        )
        return JsonResponse(serialize_comment(comment), status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(["GET"])
def api_tags(request):
    """태그 목록 조회"""
    tags = Tag.objects.all()
    return JsonResponse({
        'tags': [{'id': tag.id, 'name': tag.name} for tag in tags]
    })
