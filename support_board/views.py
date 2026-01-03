from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .services import ViteManifestService


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
