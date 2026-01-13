import json
import logging
import uuid as uuid_module
from pathlib import Path
from typing import Optional, Tuple
from dataclasses import dataclass

from django.conf import settings
from django.http import HttpRequest

logger = logging.getLogger(__name__)


@dataclass
class UserSyncResult:
    """유저 동기화 결과.

    Attributes:
        user: 동기화된 User 객체.
        created: 새로 생성 여부.
    """
    user: 'User'
    created: bool


class UserSyncService:
    """유저 동기화를 담당하는 서비스 클래스.

    WebSocket에서 받은 유저 정보를 DB와 세션에 동기화합니다.
    """

    @staticmethod
    def sync_user(validated_data: dict) -> Tuple['User', bool]:
        """유저 정보를 DB에 동기화합니다.

        Args:
            validated_data: 검증된 유저 데이터 (user_id, username, is_admin).

        Returns:
            (User 객체, 새로 생성 여부) 튜플.

        Raises:
            ValueError: user_id를 UUID로 변환할 수 없는 경우.
        """
        from .models import User

        user_id = validated_data['user_id']
        username = validated_data['username']
        is_admin = validated_data['is_admin']

        # UUID 변환
        try:
            uuid_obj = uuid_module.UUID(str(user_id))
        except ValueError:
            raise ValueError(f"user_id를 UUID로 변환할 수 없습니다: {user_id}")

        # DB에 유저 생성 또는 업데이트
        user, created = User.objects.update_or_create(
            uuid=uuid_obj,
            defaults={
                'username': username,
                'is_admin': is_admin,
            }
        )

        action = '생성' if created else '업데이트'
        logger.info(f"유저 동기화 {action}: {user.username} ({user.uuid})")

        return user, created

    @staticmethod
    def save_to_session(request: HttpRequest, user: 'User') -> None:
        """유저 정보를 세션에 저장합니다.

        Args:
            request: HTTP 요청 객체.
            user: 저장할 User 객체.
        """
        request.session['user_uuid'] = str(user.uuid)
        request.session['username'] = user.username
        request.session['is_admin'] = user.is_admin


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
