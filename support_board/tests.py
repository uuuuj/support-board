"""Support Board API 테스트.

Django REST Framework APITestCase를 사용한 API 테스트입니다.
"""

import uuid
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status

from .models import User, Post, Comment, Tag


class UserSyncAPITest(APITestCase):
    """유저 동기화 API 테스트."""

    def test_sync_new_user(self):
        """새 유저 생성 테스트."""
        user_id = str(uuid.uuid4())
        data = {
            'user_id': user_id,
            'username': '테스트유저',
            'is_admin': False,
        }

        response = self.client.post('/support/api/users/sync/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], '테스트유저')
        self.assertFalse(response.data['is_admin'])

        # DB에 저장 확인
        self.assertTrue(User.objects.filter(uuid=user_id).exists())

    def test_sync_existing_user(self):
        """기존 유저 업데이트 테스트."""
        user_id = uuid.uuid4()
        User.objects.create(uuid=user_id, username='기존유저', is_admin=False)

        data = {
            'user_id': str(user_id),
            'username': '업데이트유저',
            'is_admin': True,
        }

        response = self.client.post('/support/api/users/sync/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], '업데이트유저')
        self.assertTrue(response.data['is_admin'])

    def test_sync_missing_user_id(self):
        """user_id 누락 시 에러 테스트."""
        data = {
            'username': '테스트유저',
        }

        response = self.client.post('/support/api/users/sync/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sync_missing_username(self):
        """username 누락 시 에러 테스트."""
        data = {
            'user_id': str(uuid.uuid4()),
        }

        response = self.client.post('/support/api/users/sync/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sync_saves_to_session(self):
        """세션에 유저 정보 저장 확인 테스트."""
        user_id = str(uuid.uuid4())
        data = {
            'user_id': user_id,
            'username': '세션테스트',
            'is_admin': False,
        }

        self.client.post('/support/api/users/sync/', data, format='json')

        # /api/users/me/로 세션 확인
        response = self.client.get('/support/api/users/me/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], '세션테스트')


class PostAPITest(APITestCase):
    """게시글 API 테스트."""

    def setUp(self):
        """테스트 데이터 설정."""
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

        response = self.client.post('/support/api/posts/create/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], '테스트 제목')
        self.assertFalse(response.data['is_private'])

    def test_create_private_post_without_login(self):
        """미로그인 상태에서 비밀글 생성 시 에러 테스트."""
        data = {
            'title': '비밀글 제목',
            'content': '비밀글 내용',
            'author': '작성자',
            'is_private': True,
        }

        response = self.client.post('/support/api/posts/create/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_private_post_with_login(self):
        """로그인 상태에서 비밀글 생성 테스트."""
        self._login_as(self.user)

        data = {
            'title': '비밀글 제목',
            'content': '비밀글 내용',
            'author': '작성자',
            'is_private': True,
        }

        response = self.client.post('/support/api/posts/create/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['is_private'])

    def test_list_posts(self):
        """게시글 목록 조회 테스트."""
        Post.objects.create(title='게시글1', content='내용1', author='작성자1')
        Post.objects.create(title='게시글2', content='내용2', author='작성자2')

        response = self.client.get('/support/api/posts/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_search_posts(self):
        """게시글 검색 테스트."""
        Post.objects.create(title='Django 튜토리얼', content='내용', author='작성자')
        Post.objects.create(title='React 가이드', content='내용', author='작성자')

        response = self.client.get('/support/api/posts/', {'q': 'Django'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['posts'][0]['title'], 'Django 튜토리얼')


class PrivatePostAccessTest(APITestCase):
    """비밀글 접근 권한 테스트."""

    def setUp(self):
        """테스트 데이터 설정."""
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

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], '비밀글')

    def test_admin_can_access_private_post(self):
        """관리자는 비밀글 접근 가능."""
        self._login_as(self.admin)

        response = self.client.get(f'/support/api/posts/{self.private_post.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], '비밀글')

    def test_other_user_cannot_access_private_post(self):
        """타인은 비밀글 접근 불가."""
        self._login_as(self.other_user)

        response = self.client.get(f'/support/api/posts/{self.private_post.id}/')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_cannot_access_private_post(self):
        """비로그인 유저는 비밀글 접근 불가."""
        response = self.client.get(f'/support/api/posts/{self.private_post.id}/')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_private_post_hidden_in_list(self):
        """비밀글은 목록에서 제목/내용 숨김."""
        response = self.client.get('/support/api/posts/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        post_data = response.data['posts'][0]
        self.assertEqual(post_data['title'], '비밀글입니다.')
        self.assertEqual(post_data['content'], '')


class CommentAPITest(APITestCase):
    """댓글 API 테스트."""

    def setUp(self):
        """테스트 데이터 설정."""
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
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], '댓글 내용')

    def test_author_can_comment_on_private_post(self):
        """비밀글 작성자는 댓글 작성 가능."""
        self._login_as(self.user)

        data = {
            'content': '작성자 댓글',
            'author': '작성자',
        }

        response = self.client.post(
            f'/support/api/posts/{self.private_post.id}/comments/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_can_comment_on_private_post(self):
        """관리자는 비밀글에 댓글 작성 가능."""
        self._login_as(self.admin)

        data = {
            'content': '관리자 댓글',
            'author': '관리자',
        }

        response = self.client.post(
            f'/support/api/posts/{self.private_post.id}/comments/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_other_user_cannot_comment_on_private_post(self):
        """타인은 비밀글에 댓글 작성 불가."""
        self._login_as(self.other_user)

        data = {
            'content': '타인 댓글',
            'author': '타인',
        }

        response = self.client.post(
            f'/support/api/posts/{self.private_post.id}/comments/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_cannot_comment_on_private_post(self):
        """비로그인 유저는 비밀글에 댓글 작성 불가."""
        data = {
            'content': '익명 댓글',
            'author': '익명',
        }

        response = self.client.post(
            f'/support/api/posts/{self.private_post.id}/comments/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ValidationTest(TestCase):
    """입력값 검증 테스트."""

    def test_xss_prevention(self):
        """XSS 방지 테스트."""
        from .validators import ValidationService

        malicious_input = '<script>alert("xss")</script>'
        sanitized = ValidationService.sanitize_string(malicious_input, 200, 'test')

        self.assertNotIn('<script>', sanitized)
        self.assertIn('&lt;script&gt;', sanitized)

    def test_title_length_limit(self):
        """제목 길이 제한 테스트."""
        from .validators import ValidationService, ValidationError

        long_title = 'a' * 201

        with self.assertRaises(ValidationError):
            ValidationService.sanitize_string(long_title, 200, '제목')

    def test_tags_count_limit(self):
        """태그 개수 제한 테스트."""
        from .validators import ValidationService, ValidationError

        too_many_tags = ['tag' + str(i) for i in range(11)]

        with self.assertRaises(ValidationError):
            ValidationService.sanitize_tags(too_many_tags)
