"""API 직렬화 모듈.

Django REST Framework Serializer를 사용하여
모델 데이터의 직렬화/역직렬화를 처리합니다.
"""

from rest_framework import serializers
from .models import Post, Comment, Tag


class TagSerializer(serializers.ModelSerializer):
    """태그 직렬화."""

    class Meta:
        model = Tag
        fields = ['id', 'name']


class CommentSerializer(serializers.ModelSerializer):
    """댓글 직렬화."""

    class Meta:
        model = Comment
        fields = [
            'id', 'content', 'user_name', 'user_id',
            'user_compname', 'user_deptname', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CommentCreateSerializer(serializers.Serializer):
    """댓글 생성 요청 직렬화."""

    content = serializers.CharField(
        max_length=10000,
        help_text='댓글 내용 (최대 10000자)'
    )
    user_name = serializers.CharField(
        max_length=50,
        required=False,
        default='Anonymous',
        help_text='작성자 (기본값: Anonymous)'
    )


class PostListSerializer(serializers.ModelSerializer):
    """게시글 목록 직렬화."""

    tags = serializers.StringRelatedField(many=True, read_only=True)
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'user_name', 'user_id',
            'user_compname', 'user_deptname',
            'tags', 'is_resolved', 'is_private', 'comments_count',
            'created_at', 'updated_at'
        ]


class PostDetailSerializer(serializers.ModelSerializer):
    """게시글 상세 직렬화 (댓글 포함)."""

    tags = serializers.StringRelatedField(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'user_name', 'user_id',
            'user_compname', 'user_deptname',
            'tags', 'is_resolved', 'is_private', 'comments_count',
            'comments', 'created_at', 'updated_at'
        ]


class PostCreateSerializer(serializers.Serializer):
    """게시글 생성 요청 직렬화."""

    title = serializers.CharField(
        max_length=200,
        help_text='게시글 제목 (최대 200자)'
    )
    content = serializers.CharField(
        max_length=10000,
        help_text='게시글 내용 (최대 10000자)'
    )
    user_name = serializers.CharField(
        max_length=50,
        required=False,
        default='Anonymous',
        help_text='작성자 (기본값: Anonymous)'
    )
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        default=list,
        help_text='태그 목록 (최대 10개)'
    )
    is_resolved = serializers.BooleanField(
        required=False,
        default=False,
        help_text='해결 여부'
    )
    is_private = serializers.BooleanField(
        required=False,
        default=False,
        help_text='비밀글 여부 (로그인 필요)'
    )


class PostUpdateSerializer(serializers.Serializer):
    """게시글 수정 요청 직렬화."""

    title = serializers.CharField(
        max_length=200,
        required=False,
        help_text='게시글 제목 (최대 200자)'
    )
    content = serializers.CharField(
        max_length=10000,
        required=False,
        help_text='게시글 내용 (최대 10000자)'
    )
    user_name = serializers.CharField(
        max_length=50,
        required=False,
        help_text='작성자'
    )
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        help_text='태그 목록 (최대 10개)'
    )
    is_resolved = serializers.BooleanField(
        required=False,
        help_text='해결 여부'
    )
    is_private = serializers.BooleanField(
        required=False,
        help_text='비밀글 여부'
    )


class ErrorSerializer(serializers.Serializer):
    """에러 응답 직렬화."""

    error = serializers.CharField(help_text='에러 메시지')


class MessageSerializer(serializers.Serializer):
    """성공 메시지 응답 직렬화."""

    message = serializers.CharField(help_text='결과 메시지')
