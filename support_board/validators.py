"""입력값 검증 및 sanitization 모듈.

이 모듈은 SQL Injection, XSS 등의 보안 공격을 방지하기 위한
입력값 검증 및 sanitization 기능을 제공합니다.
"""

import html
import re
import logging
from typing import List, Optional, Any

logger = logging.getLogger(__name__)


# 입력값 제한 상수
MAX_TITLE_LENGTH = 200
MAX_CONTENT_LENGTH = 10000
MAX_AUTHOR_LENGTH = 50
MAX_TAG_LENGTH = 50
MAX_TAGS_COUNT = 10
MAX_JSON_SIZE = 50 * 1024  # 50KB


class ValidationError(Exception):
    """입력값 검증 오류.

    사용자 입력값이 유효하지 않을 때 발생하는 예외입니다.

    Attributes:
        message: 에러 메시지.
        field: 오류가 발생한 필드명.
    """

    def __init__(self, message: str, field: Optional[str] = None):
        """ValidationError를 초기화합니다.

        Args:
            message: 에러 메시지.
            field: 오류가 발생한 필드명 (선택).
        """
        self.message = message
        self.field = field
        super().__init__(message)


class ValidationService:
    """입력값 검증 및 sanitization을 담당하는 서비스 클래스.

    SQL Injection, XSS 등의 보안 공격을 방지하기 위해
    모든 사용자 입력값을 검증하고 sanitize합니다.

    Example:
        >>> service = ValidationService()
        >>> clean_title = service.sanitize_string(
        ...     "<script>alert('xss')</script>",
        ...     max_length=200,
        ...     field_name="제목"
        ... )
        >>> print(clean_title)
        &lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;
    """

    @staticmethod
    def sanitize_string(
        value: Any,
        max_length: int,
        field_name: str,
        allow_empty: bool = False
    ) -> str:
        """문자열 입력값을 검증하고 sanitize합니다.

        XSS 방지를 위해 HTML 특수문자를 이스케이프하고,
        길이 제한 및 빈 값 검증을 수행합니다.

        Args:
            value: 검증할 입력값.
            max_length: 최대 허용 길이.
            field_name: 필드명 (에러 메시지용).
            allow_empty: 빈 값 허용 여부 (기본값: False).

        Returns:
            sanitize된 문자열.

        Raises:
            ValidationError: 입력값이 유효하지 않은 경우.
        """
        # 타입 검증
        if value is None:
            if allow_empty:
                return ""
            raise ValidationError(f"{field_name}은(는) 필수 입력 항목입니다.", field_name)

        if not isinstance(value, str):
            raise ValidationError(f"{field_name}은(는) 문자열이어야 합니다.", field_name)

        # 앞뒤 공백 제거
        value = value.strip()

        # 빈 값 검증
        if not allow_empty and not value:
            raise ValidationError(f"{field_name}은(는) 필수 입력 항목입니다.", field_name)

        # 길이 제한
        if len(value) > max_length:
            raise ValidationError(
                f"{field_name}은(는) {max_length}자를 초과할 수 없습니다.",
                field_name
            )

        # XSS 방지: HTML 특수문자 이스케이프
        value = html.escape(value)

        return value

    @staticmethod
    def sanitize_tags(tags: Any) -> List[str]:
        """태그 목록을 검증하고 sanitize합니다.

        Args:
            tags: 검증할 태그 목록.

        Returns:
            sanitize된 태그 목록.

        Raises:
            ValidationError: 태그 목록이 유효하지 않은 경우.
        """
        if tags is None:
            return []

        if not isinstance(tags, list):
            raise ValidationError("태그는 배열 형식이어야 합니다.", "tags")

        if len(tags) > MAX_TAGS_COUNT:
            raise ValidationError(
                f"태그는 최대 {MAX_TAGS_COUNT}개까지 가능합니다.",
                "tags"
            )

        sanitized_tags = []
        for tag in tags:
            if isinstance(tag, str):
                tag = tag.strip()
                if tag:  # 빈 태그 제외
                    if len(tag) > MAX_TAG_LENGTH:
                        raise ValidationError(
                            f"태그는 {MAX_TAG_LENGTH}자를 초과할 수 없습니다.",
                            "tags"
                        )
                    sanitized_tags.append(html.escape(tag))

        return sanitized_tags

    @staticmethod
    def validate_boolean(value: Any, default: bool = False) -> bool:
        """불리언 값을 검증합니다.

        Args:
            value: 검증할 값.
            default: 기본값 (기본값: False).

        Returns:
            검증된 불리언 값.
        """
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() == "true"
        return default

    @classmethod
    def validate_post_data(cls, data: dict, is_update: bool = False) -> dict:
        """게시글 데이터를 검증하고 sanitize합니다.

        Args:
            data: 검증할 게시글 데이터.
            is_update: 수정 요청 여부 (기본값: False).

        Returns:
            검증 및 sanitize된 데이터.

        Raises:
            ValidationError: 데이터가 유효하지 않은 경우.
        """
        validated = {}

        # 생성 시에는 필수, 수정 시에는 선택
        if "title" in data or not is_update:
            validated["title"] = cls.sanitize_string(
                data.get("title"),
                MAX_TITLE_LENGTH,
                "제목",
                allow_empty=is_update
            )

        if "content" in data or not is_update:
            validated["content"] = cls.sanitize_string(
                data.get("content"),
                MAX_CONTENT_LENGTH,
                "내용",
                allow_empty=is_update
            )

        if "author" in data or not is_update:
            validated["author"] = cls.sanitize_string(
                data.get("author", "Anonymous"),
                MAX_AUTHOR_LENGTH,
                "작성자",
                allow_empty=True
            ) or "Anonymous"

        if "tags" in data:
            validated["tags"] = cls.sanitize_tags(data.get("tags"))

        if "is_resolved" in data:
            validated["is_resolved"] = cls.validate_boolean(data.get("is_resolved"))

        return validated

    @classmethod
    def validate_comment_data(cls, data: dict) -> dict:
        """댓글 데이터를 검증하고 sanitize합니다.

        Args:
            data: 검증할 댓글 데이터.

        Returns:
            검증 및 sanitize된 데이터.

        Raises:
            ValidationError: 데이터가 유효하지 않은 경우.
        """
        return {
            "content": cls.sanitize_string(
                data.get("content"),
                MAX_CONTENT_LENGTH,
                "내용"
            ),
            "author": cls.sanitize_string(
                data.get("author", "Anonymous"),
                MAX_AUTHOR_LENGTH,
                "작성자",
                allow_empty=True
            ) or "Anonymous",
        }

    @staticmethod
    def validate_json_size(body: bytes) -> None:
        """JSON 요청 본문의 크기를 검증합니다.

        Args:
            body: 요청 본문.

        Raises:
            ValidationError: 요청 본문이 너무 큰 경우.
        """
        if len(body) > MAX_JSON_SIZE:
            raise ValidationError(
                f"요청 데이터가 너무 큽니다. (최대 {MAX_JSON_SIZE // 1024}KB)"
            )
