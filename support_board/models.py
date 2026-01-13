import uuid
from django.db import models
from django.contrib.auth.hashers import make_password, check_password


class User(models.Model):
    """사용자 모델.

    Attributes:
        uuid: 사용자 고유 식별자 (Primary Key).
        username: 로그인 ID (고유).
        password: 해시된 비밀번호.
        is_admin: 관리자 여부.
        created_at: 생성 일시.
    """

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)  # 해시된 비밀번호 저장
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.username

    def set_password(self, raw_password: str) -> None:
        """비밀번호를 해시하여 저장합니다.

        Args:
            raw_password: 평문 비밀번호.
        """
        self.password = make_password(raw_password)

    def check_password(self, raw_password: str) -> bool:
        """비밀번호가 일치하는지 확인합니다.

        Args:
            raw_password: 확인할 평문 비밀번호.

        Returns:
            비밀번호 일치 여부.
        """
        return check_password(raw_password, self.password)


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Post(models.Model):
    """게시글 모델.

    Attributes:
        title: 게시글 제목.
        content: 게시글 내용.
        author: 작성자 이름 (표시용).
        user: 작성자 User 객체 (비밀글 권한 확인용).
        tags: 태그 목록.
        is_resolved: 해결 여부.
        is_private: 비밀글 여부.
        created_at: 생성 일시.
        updated_at: 수정 일시.
    """

    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.CharField(max_length=50)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts'
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    is_resolved = models.BooleanField(default=False)
    is_private = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def can_access(self, user: 'User | None') -> bool:
        """사용자가 이 게시글에 접근할 수 있는지 확인합니다.

        Args:
            user: 접근하려는 사용자 (None이면 비로그인 사용자).

        Returns:
            접근 가능 여부.
        """
        # 비밀글이 아니면 모두 접근 가능
        if not self.is_private:
            return True

        # 비밀글인 경우
        if user is None:
            return False

        # 관리자이거나 작성자 본인이면 접근 가능
        return user.is_admin or self.user == user


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    author = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.author}: {self.content[:20]}'
