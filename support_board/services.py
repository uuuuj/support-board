import json
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

from django.conf import settings


@dataclass
class ViteManifestEntry:
    """Vite manifest에서 파싱된 엔트리 정보.

    Attributes:
        js_file: JavaScript 파일 경로.
        css_file: CSS 파일 경로.
    """
    js_file: Optional[str] = None
    css_file: Optional[str] = None


class ViteManifestService:
    """Vite manifest 파일을 파싱하는 서비스 클래스.

    React 빌드 결과물의 manifest.json을 읽어서
    JavaScript와 CSS 파일 경로를 추출합니다.

    Attributes:
        manifest_path: manifest.json 파일의 경로.
        entry_point: manifest에서 찾을 엔트리 포인트 키.
    """

    def __init__(
        self,
        manifest_path: Optional[Path] = None,
        entry_point: str = 'src/main.jsx'
    ):
        """ViteManifestService를 초기화합니다.

        Args:
            manifest_path: manifest.json 파일 경로
                (기본값: support_board/static/support_board/.vite/manifest.json).
            entry_point: manifest에서 찾을 엔트리 포인트 키 (기본값: 'src/main.jsx').
        """
        self.manifest_path = manifest_path or (
            Path(settings.BASE_DIR) / 'support_board' / 'static' / 'support_board' / '.vite' / 'manifest.json'
        )
        self.entry_point = entry_point

    def get_entry(self) -> ViteManifestEntry:
        """manifest에서 엔트리 포인트의 파일 정보를 추출합니다.

        Returns:
            ViteManifestEntry: JS와 CSS 파일 경로가 담긴 객체.
                manifest 파일이 없거나 파싱 실패 시 빈 값을 가진 객체 반환.
        """
        if not self.manifest_path.exists():
            return ViteManifestEntry()

        try:
            with open(self.manifest_path, encoding='utf-8') as f:
                manifest = json.load(f)
        except (json.JSONDecodeError, OSError):
            return ViteManifestEntry()

        entry = manifest.get(self.entry_point, {})
        css_files = entry.get('css', [])

        return ViteManifestEntry(
            js_file=entry.get('file'),
            css_file=css_files[0] if css_files else None,
        )
