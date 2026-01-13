"""Support Board API 테스트.

Django TestCase를 사용한 API 테스트입니다.
"""

import json
import uuid
from django.test import TestCase, Client

from support_board.models import User, Post, Comment, Tag


class TestResults:
    """테스트 결과 저장"""
    items = []

    @classmethod
    def add(cls, name, status):
        cls.items.append((name, status))

    @classmethod
    def print_summary(cls):
        print("\n" + "=" * 50)
        print("API 테스트 결과 요약")
        print("=" * 50)
        for name, status in cls.items:
            icon = "PASS" if status == "PASS" else "FAIL"
            print(f"[{icon}] {name}")
        print("=" * 50)
        cls.items = []


class UserSyncAPITest(TestCase):
    """유저 동기화 API 테스트."""

    def setUp(self):
        self.client = Client()

    def test_sync_new_user(self):
        """새 유저 생성 테스트."""
        user_id = str(uuid.uuid4())
        data = {
            'user_id': user_id,
            'username': '테스트유저',
            'is_admin': False,
        }

        response = self.client.post(
            '/support/api/users/sync/',
            json.dumps(data),
            content_type='application/json'
        )

        try:
            self.assertEqual(response.status_code, 201)
            result = response.json()
            self.assertEqual(result['username'], '테스트유저')
            self.assertFalse(result['is_admin'])
            self.assertTrue(User.objects.filter(uuid=user_id).exists())
            TestResults.add("test_sync_new_user", "PASS")
        except AssertionError:
            TestResults.add("test_sync_new_user", "FAIL")
            raise

    def test_sync_existing_user(self):
        """기존 유저 업데이트 테스트."""
        user_id = uuid.uuid4()
        User.objects.create(uuid=user_id, username='기존유저', is_admin=False)

        data = {
            'user_id': str(user_id),
            'username': '업데이트유저',
            'is_admin': True,
        }

        response = self.client.post(
            '/support/api/users/sync/',
            json.dumps(data),
            content_type='application/json'
        )

        try:
            self.assertEqual(response.status_code, 200)
            result = response.json()
            self.assertEqual(result['username'], '업데이트유저')
            self.assertTrue(result['is_admin'])
            TestResults.add("test_sync_existing_user", "PASS")
        except AssertionError:
            TestResults.add("test_sync_existing_user", "FAIL")
            raise

    def test_sync_missing_user_id(self):
        """user_id 누락 시 에러 테스트."""
        data = {
            'username': '테스트유저',
        }

        response = self.client.post(
            '/support/api/users/sync/',
            json.dumps(data),
            content_type='application/json'
        )

        try:
            self.assertEqual(response.status_code, 400)
            TestResults.add("test_sync_missing_user_id", "PASS")
        except AssertionError:
            TestResults.add("test_sync_missing_user_id", "FAIL")
            raise

    def test_sync_missing_username(self):
        """username 누락 시 에러 테스트."""
        data = {
            'user_id': str(uuid.uuid4()),
        }

        response = self.client.post(
            '/support/api/users/sync/',
            json.dumps(data),
            content_type='application/json'
        )

        try:
            self.assertEqual(response.status_code, 400)
            TestResults.add("test_sync_missing_username", "PASS")
        except AssertionError:
            TestResults.add("test_sync_missing_username", "FAIL")
            raise

    def test_sync_saves_to_session(self):
        """세션에 유저 정보 저장 확인 테스트."""
        user_id = str(uuid.uuid4())
        data = {
            'user_id': user_id,
            'username': '세션테스트',
            'is_admin': False,
        }

        self.client.post(
            '/support/api/users/sync/',
            json.dumps(data),
            content_type='application/json'
        )

        response = self.client.get('/support/api/users/me/')

        try:
            self.assertEqual(response.status_code, 200)
            result = response.json()
            self.assertEqual(result['username'], '세션테스트')
            TestResults.add("test_sync_saves_to_session", "PASS")
        except AssertionError:
            TestResults.add("test_sync_saves_to_session", "FAIL")
            raise


class PostAPITest(TestCase):
    """게시글 API 테스트."""

    def setUp(self):
        """테스트 데이터 설정."""
        self.client = Client()
        self.user = User.objects.create(
            uuid=uuid.uuid4(),
            username='testuser',
            is_admin=False,
        )
        self.admin = User.objects.create(
            uuid=uuid.uuid4(),
            username='adminuser',
            is_admin=True,
        )
        self.other_user = User.objects.create(
            uuid=uuid.uuid4(),
            username='otheruser',
            is_admin=False,
        )

    def _login_as(self, user):
        """특정 유저로 로그인 (세션 설정)."""
        session = self.client.session
        session['user_uuid'] = str(user.uuid)
        session['username'] = user.username
        session['is_admin'] = user.is_admin
        session.save()

    def test_create_post(self):
        """일반 게시글 생성 테스트."""
        data = {
            'title': '테스트 제목',
            'content': '테스트 내용',
            'author': '작성자',
        }

        response = self.client.post(
            '/support/api/posts/create/',
            json.dumps(data),
            content_type='application/json'
        )

        try:
            self.assertEqual(response.status_code, 201)
            result = response.json()
            self.assertEqual(result['title'], '테스트 제목')
            self.assertFalse(result['is_private'])
            TestResults.add("test_create_post", "PASS")
        except AssertionError:
            TestResults.add("test_create_post", "FAIL")
            raise

    def test_create_private_post_without_login(self):
        """미로그인 상태에서 비밀글 생성 시 에러 테스트."""
        data = {
            'title': '비밀글 제목',
            'content': '비밀글 내용',
            'author': '작성자',
            'is_private': True,
        }

        response = self.client.post(
            '/support/api/posts/create/',
            json.dumps(data),
            content_type='application/json'
        )

        try:
            self.assertEqual(response.status_code, 401)
            TestResults.add("test_create_private_post_without_login", "PASS")
        except AssertionError:
            TestResults.add("test_create_private_post_without_login", "FAIL")
            raise

    def test_create_private_post_with_login(self):
        """로그인 상태에서 비밀글 생성 테스트."""
        self._login_as(self.user)

        data = {
            'title': '비밀글 제목',
            'content': '비밀글 내용',
            'author': '작성자',
            'is_private': True,
        }

        response = self.client.post(
            '/support/api/posts/create/',
            json.dumps(data),
            content_type='application/json'
        )

        try:
            self.assertEqual(response.status_code, 201)
            result = response.json()
            self.assertTrue(result['is_private'])
            TestResults.add("test_create_private_post_with_login", "PASS")
        except AssertionError:
            TestResults.add("test_create_private_post_with_login", "FAIL")
            raise

    def test_list_posts(self):
        """게시글 목록 조회 테스트."""
        Post.objects.create(title='게시글1', content='내용1', author='작성자1')
        Post.objects.create(title='게시글2', content='내용2', author='작성자2')

        response = self.client.get('/support/api/posts/')

        try:
            self.assertEqual(response.status_code, 200)
            result = response.json()
            self.assertEqual(result['count'], 2)
            TestResults.add("test_list_posts", "PASS")
        except AssertionError:
            TestResults.add("test_list_posts", "FAIL")
            raise

    def test_search_posts(self):
        """게시글 검색 테스트."""
        Post.objects.create(title='Django 튜토리얼', content='내용', author='작성자')
        Post.objects.create(title='React 가이드', content='내용', author='작성자')

        response = self.client.get('/support/api/posts/', {'q': 'Django'})

        try:
            self.assertEqual(response.status_code, 200)
            result = response.json()
            self.assertEqual(result['count'], 1)
            self.assertEqual(result['posts'][0]['title'], 'Django 튜토리얼')
            TestResults.add("test_search_posts", "PASS")
        except AssertionError:
            TestResults.add("test_search_posts", "FAIL")
            raise


class PrivatePostAccessTest(TestCase):
    """비밀글 접근 권한 테스트."""

    def setUp(self):
        """테스트 데이터 설정."""
        self.client = Client()
        self.author = User.objects.create(
            uuid=uuid.uuid4(),
            username='author',
            is_admin=False,
        )
        self.admin = User.objects.create(
            uuid=uuid.uuid4(),
            username='admin',
            is_admin=True,
        )
        self.other_user = User.objects.create(
            uuid=uuid.uuid4(),
            username='other',
            is_admin=False,
        )

        self.private_post = Post.objects.create(
            title='비밀글',
            content='비밀 내용',
            author='작성자',
            user=self.author,
            is_private=True,
        )

    def _login_as(self, user):
        """특정 유저로 로그인 (세션 설정)."""
        session = self.client.session
        session['user_uuid'] = str(user.uuid)
        session['username'] = user.username
        session['is_admin'] = user.is_admin
        session.save()

    def test_author_can_access_private_post(self):
        """작성자는 비밀글 접근 가능."""
        self._login_as(self.author)

        response = self.client.get(f'/support/api/posts/{self.private_post.id}/')

        try:
            self.assertEqual(response.status_code, 200)
            result = response.json()
            self.assertEqual(result['title'], '비밀글')
            TestResults.add("test_author_can_access_private_post", "PASS")
        except AssertionError:
            TestResults.add("test_author_can_access_private_post", "FAIL")
            raise

    def test_admin_can_access_private_post(self):
        """관리자는 비밀글 접근 가능."""
        self._login_as(self.admin)

        response = self.client.get(f'/support/api/posts/{self.private_post.id}/')

        try:
            self.assertEqual(response.status_code, 200)
            result = response.json()
            self.assertEqual(result['title'], '비밀글')
            TestResults.add("test_admin_can_access_private_post", "PASS")
        except AssertionError:
            TestResults.add("test_admin_can_access_private_post", "FAIL")
            raise

    def test_other_user_cannot_access_private_post(self):
        """타인은 비밀글 접근 불가."""
        self._login_as(self.other_user)

        response = self.client.get(f'/support/api/posts/{self.private_post.id}/')

        try:
            self.assertEqual(response.status_code, 403)
            TestResults.add("test_other_user_cannot_access_private_post", "PASS")
        except AssertionError:
            TestResults.add("test_other_user_cannot_access_private_post", "FAIL")
            raise

    def test_anonymous_cannot_access_private_post(self):
        """비로그인 유저는 비밀글 접근 불가."""
        response = self.client.get(f'/support/api/posts/{self.private_post.id}/')

        try:
            self.assertEqual(response.status_code, 403)
            TestResults.add("test_anonymous_cannot_access_private_post", "PASS")
        except AssertionError:
            TestResults.add("test_anonymous_cannot_access_private_post", "FAIL")
            raise

    def test_private_post_hidden_in_list(self):
        """비밀글은 목록에서 제목/내용 숨김."""
        response = self.client.get('/support/api/posts/')

        try:
            self.assertEqual(response.status_code, 200)
            result = response.json()
            post_data = result['posts'][0]
            self.assertEqual(post_data['title'], '비밀글입니다.')
            self.assertEqual(post_data['content'], '')
            TestResults.add("test_private_post_hidden_in_list", "PASS")
        except AssertionError:
            TestResults.add("test_private_post_hidden_in_list", "FAIL")
            raise


class CommentAPITest(TestCase):
    """댓글 API 테스트."""

    def setUp(self):
        """테스트 데이터 설정."""
        self.client = Client()
        self.user = User.objects.create(
            uuid=uuid.uuid4(),
            username='testuser',
            is_admin=False,
        )
        self.admin = User.objects.create(
            uuid=uuid.uuid4(),
            username='adminuser',
            is_admin=True,
        )
        self.other_user = User.objects.create(
            uuid=uuid.uuid4(),
            username='otheruser',
            is_admin=False,
        )

        self.public_post = Post.objects.create(
            title='공개글',
            content='내용',
            author='작성자',
        )
        self.private_post = Post.objects.create(
            title='비밀글',
            content='비밀 내용',
            author='작성자',
            user=self.user,
            is_private=True,
        )

    def _login_as(self, user):
        """특정 유저로 로그인 (세션 설정)."""
        session = self.client.session
        session['user_uuid'] = str(user.uuid)
        session['username'] = user.username
        session['is_admin'] = user.is_admin
        session.save()

    def test_create_comment_on_public_post(self):
        """공개글에 댓글 작성 테스트."""
        data = {
            'content': '댓글 내용',
            'author': '댓글작성자',
        }

        response = self.client.post(
            f'/support/api/posts/{self.public_post.id}/comments/',
            json.dumps(data),
            content_type='application/json'
        )

        try:
            self.assertEqual(response.status_code, 201)
            result = response.json()
            self.assertEqual(result['content'], '댓글 내용')
            TestResults.add("test_create_comment_on_public_post", "PASS")
        except AssertionError:
            TestResults.add("test_create_comment_on_public_post", "FAIL")
            raise

    def test_author_can_comment_on_private_post(self):
        """비밀글 작성자는 댓글 작성 가능."""
        self._login_as(self.user)

        data = {
            'content': '작성자 댓글',
            'author': '작성자',
        }

        response = self.client.post(
            f'/support/api/posts/{self.private_post.id}/comments/',
            json.dumps(data),
            content_type='application/json'
        )

        try:
            self.assertEqual(response.status_code, 201)
            TestResults.add("test_author_can_comment_on_private_post", "PASS")
        except AssertionError:
            TestResults.add("test_author_can_comment_on_private_post", "FAIL")
            raise

    def test_admin_can_comment_on_private_post(self):
        """관리자는 비밀글에 댓글 작성 가능."""
        self._login_as(self.admin)

        data = {
            'content': '관리자 댓글',
            'author': '관리자',
        }

        response = self.client.post(
            f'/support/api/posts/{self.private_post.id}/comments/',
            json.dumps(data),
            content_type='application/json'
        )

        try:
            self.assertEqual(response.status_code, 201)
            TestResults.add("test_admin_can_comment_on_private_post", "PASS")
        except AssertionError:
            TestResults.add("test_admin_can_comment_on_private_post", "FAIL")
            raise

    def test_other_user_cannot_comment_on_private_post(self):
        """타인은 비밀글에 댓글 작성 불가."""
        self._login_as(self.other_user)

        data = {
            'content': '타인 댓글',
            'author': '타인',
        }

        response = self.client.post(
            f'/support/api/posts/{self.private_post.id}/comments/',
            json.dumps(data),
            content_type='application/json'
        )

        try:
            self.assertEqual(response.status_code, 403)
            TestResults.add("test_other_user_cannot_comment_on_private_post", "PASS")
        except AssertionError:
            TestResults.add("test_other_user_cannot_comment_on_private_post", "FAIL")
            raise

    def test_anonymous_cannot_comment_on_private_post(self):
        """비로그인 유저는 비밀글에 댓글 작성 불가."""
        data = {
            'content': '익명 댓글',
            'author': '익명',
        }

        response = self.client.post(
            f'/support/api/posts/{self.private_post.id}/comments/',
            json.dumps(data),
            content_type='application/json'
        )

        try:
            self.assertEqual(response.status_code, 403)
            TestResults.add("test_anonymous_cannot_comment_on_private_post", "PASS")
        except AssertionError:
            TestResults.add("test_anonymous_cannot_comment_on_private_post", "FAIL")
            raise

    @classmethod
    def tearDownClass(cls):
        """마지막 테스트 클래스 끝나면 요약 출력"""
        super().tearDownClass()
        TestResults.print_summary()


class ValidationTest(TestCase):
    """입력값 검증 테스트."""

    def test_xss_prevention(self):
        """XSS 방지 테스트."""
        from support_board.validators import ValidationService

        malicious_input = '<script>alert("xss")</script>'
        sanitized = ValidationService.sanitize_string(malicious_input, 200, 'test')

        try:
            self.assertNotIn('<script>', sanitized)
            self.assertIn('&lt;script&gt;', sanitized)
            TestResults.add("test_xss_prevention", "PASS")
        except AssertionError:
            TestResults.add("test_xss_prevention", "FAIL")
            raise

    def test_title_length_limit(self):
        """제목 길이 제한 테스트."""
        from support_board.validators import ValidationService, ValidationError

        long_title = 'a' * 201

        try:
            with self.assertRaises(ValidationError):
                ValidationService.sanitize_string(long_title, 200, '제목')
            TestResults.add("test_title_length_limit", "PASS")
        except AssertionError:
            TestResults.add("test_title_length_limit", "FAIL")
            raise

    def test_tags_count_limit(self):
        """태그 개수 제한 테스트."""
        from support_board.validators import ValidationService, ValidationError

        too_many_tags = ['tag' + str(i) for i in range(11)]

        try:
            with self.assertRaises(ValidationError):
                ValidationService.sanitize_tags(too_many_tags)
            TestResults.add("test_tags_count_limit", "PASS")
        except AssertionError:
            TestResults.add("test_tags_count_limit", "FAIL")
            raise
