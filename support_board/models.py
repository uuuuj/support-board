from django.db import models


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
        user_name: 작성자 이름 (표시용).
        user_id: 작성자 ID (외부 User 테이블 참조, FK 아님).
        user_compname: 작성자 회사명.
        user_deptname: 작성자 부서명.
        tags: 태그 목록.
        is_resolved: 해결 여부.
        is_private: 비밀글 여부.
        created_at: 생성 일시.
        updated_at: 수정 일시.
    """

    title = models.CharField(max_length=200)
    content = models.TextField()
    user_name = models.CharField(max_length=50)
    user_id = models.CharField(max_length=100, null=True, blank=True)
    user_compname = models.CharField(max_length=100, null=True, blank=True)
    user_deptname = models.CharField(max_length=100, null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    is_resolved = models.BooleanField(default=False)
    is_private = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def can_access(self, user_id: str | None, is_admin: bool = False) -> bool:
        """사용자가 이 게시글에 접근할 수 있는지 확인합니다.

        Args:
            user_id: 접근하려는 사용자의 ID (None이면 비로그인 사용자).
            is_admin: 관리자 여부 (세션에서 가져온 값).

        Returns:
            접근 가능 여부.
        """
        # 비밀글이 아니면 모두 접근 가능
        if not self.is_private:
            return True

        # 비밀글인 경우
        if user_id is None:
            return False

        # 관리자이거나 작성자 본인이면 접근 가능
        return is_admin or self.user_id == user_id


class Comment(models.Model):
    """댓글 모델.

    Attributes:
        post: 댓글이 달린 게시글.
        content: 댓글 내용.
        user_name: 작성자 이름.
        user_id: 작성자 ID (외부 User 테이블 참조, FK 아님).
        user_compname: 작성자 회사명.
        user_deptname: 작성자 부서명.
        created_at: 생성 일시.
        updated_at: 수정 일시.
    """

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    user_name = models.CharField(max_length=50)
    user_id = models.CharField(max_length=100, null=True, blank=True)
    user_compname = models.CharField(max_length=100, null=True, blank=True)
    user_deptname = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.user_name}: {self.content[:20]}'
