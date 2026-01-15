"""Support Board API 테스트.

Factory Boy + Django TestCase를 사용한 API 테스트입니다.
"""

import json
from django.test import TestCase, Client

from support_board.models import Post, Comment, Tag


class PostAPITest(TestCase):
    """게시글 API 테스트."""

    def setUp(self):
        """테스트 데이터 설정."""
        self.client = Client()

        # TODO: User factory를 사용하여 테스트 유저 생성
        # self.user = UserFactory(is_admin=False)
        # self.admin = UserFactory(is_admin=True)
        # self.other_user = UserFactory(is_admin=False)

        # 임시 유저 정보 (세션에 저장할 데이터)
        self.user_info = {
            'user_id': 'test-user-001',
            'user_name': 'testuser',
            'user_compname': '테스트회사',
            'user_deptname': '테스트부서',
            'is_admin': False,
        }
        self.admin_info = {
            'user_id': 'admin-user-001',
            'user_name': 'adminuser',
            'user_compname': '관리회사',
            'user_deptname': '관리부서',
            'is_admin': True,
        }
        self.other_user_info = {
            'user_id': 'other-user-001',
            'user_name': 'otheruser',
            'user_compname': '타사',
            'user_deptname': '타부서',
            'is_admin': False,
        }

    def _set_session(self, user_info):
        """세션에 유저 정보 설정."""
        session = self.client.session
        session['user_id'] = user_info['user_id']
        session['user_name'] = user_info['user_name']
        session['user_compname'] = user_info['user_compname']
        session['user_deptname'] = user_info['user_deptname']
        session['is_admin'] = user_info['is_admin']
        session.save()

    def test_create_post(self):
        """일반 게시글 생성 테스트."""
        data = {
            'title': '테스트 제목',
            'content': '테스트 내용',
            'user_name': '작성자',
        }

        response = self.client.post(
            '/support/api/posts/create/',
            json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)
        result = response.json()
        self.assertEqual(result['title'], '테스트 제목')
        self.assertFalse(result['is_private'])

    def test_create_private_post_without_login(self):
        """미로그인 상태에서 비밀글 생성 시 에러 테스트."""
        data = {
            'title': '비밀글 제목',
            'content': '비밀글 내용',
            'user_name': '작성자',
            'is_private': True,
        }

        response = self.client.post(
            '/support/api/posts/create/',
            json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 401)

    def test_create_private_post_with_login(self):
        """로그인 상태에서 비밀글 생성 테스트."""
        self._set_session(self.user_info)

        data = {
            'title': '비밀글 제목',
            'content': '비밀글 내용',
            'user_name': '작성자',
            'is_private': True,
        }

        response = self.client.post(
            '/support/api/posts/create/',
            json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)
        result = response.json()
        self.assertTrue(result['is_private'])

    def test_list_posts(self):
        """게시글 목록 조회 테스트."""
        Post.objects.create(title='게시글1', content='내용1', user_name='작성자1')
        Post.objects.create(title='게시글2', content='내용2', user_name='작성자2')

        response = self.client.get('/support/api/posts/')

        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result['count'], 2)

    def test_search_posts(self):
        """게시글 검색 테스트."""
        Post.objects.create(title='Django 튜토리얼', content='내용', user_name='작성자')
        Post.objects.create(title='React 가이드', content='내용', user_name='작성자')

        response = self.client.get('/support/api/posts/', {'q': 'Django'})

        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result['count'], 1)
        self.assertEqual(result['posts'][0]['title'], 'Django 튜토리얼')

    def test_create_post_with_tags(self):
        """태그와 함께 게시글 생성 테스트."""
        data = {
            'title': '태그 테스트',
            'content': '태그가 있는 게시글',
            'user_name': '작성자',
            'tags': ['Django', 'Python', 'API'],
        }

        response = self.client.post(
            '/support/api/posts/create/',
            json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)
        result = response.json()
        self.assertEqual(len(result['tags']), 3)
        self.assertIn('Django', result['tags'])

    def test_update_post(self):
        """게시글 수정 테스트."""
        self._set_session(self.user_info)

        post = Post.objects.create(
            title='원본 제목',
            content='원본 내용',
            user_name='작성자',
            user_id=self.user_info['user_id'],
        )

        data = {
            'title': '수정된 제목',
            'content': '수정된 내용',
        }

        response = self.client.put(
            f'/support/api/posts/{post.id}/update/',
            json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result['title'], '수정된 제목')

    def test_delete_post(self):
        """게시글 삭제 테스트."""
        self._set_session(self.user_info)

        post = Post.objects.create(
            title='삭제할 게시글',
            content='내용',
            user_name='작성자',
            user_id=self.user_info['user_id'],
        )

        response = self.client.delete(f'/support/api/posts/{post.id}/delete/')

        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertTrue(result['success'])
        self.assertFalse(Post.objects.filter(id=post.id).exists())


class PrivatePostAccessTest(TestCase):
    """비밀글 접근 권한 테스트."""

    def setUp(self):
        """테스트 데이터 설정."""
        self.client = Client()

        # TODO: User factory를 사용하여 테스트 유저 생성
        # self.author = UserFactory(is_admin=False)
        # self.admin = UserFactory(is_admin=True)
        # self.other_user = UserFactory(is_admin=False)

        self.author_info = {
            'user_id': 'author-001',
            'user_name': 'author',
            'user_compname': '작성자회사',
            'user_deptname': '작성자부서',
            'is_admin': False,
        }
        self.admin_info = {
            'user_id': 'admin-001',
            'user_name': 'admin',
            'user_compname': '관리회사',
            'user_deptname': '관리부서',
            'is_admin': True,
        }
        self.other_user_info = {
            'user_id': 'other-001',
            'user_name': 'other',
            'user_compname': '타회사',
            'user_deptname': '타부서',
            'is_admin': False,
        }

        self.private_post = Post.objects.create(
            title='비밀글',
            content='비밀 내용',
            user_name='작성자',
            user_id=self.author_info['user_id'],
            user_compname=self.author_info['user_compname'],
            user_deptname=self.author_info['user_deptname'],
            is_private=True,
        )

    def _set_session(self, user_info):
        """세션에 유저 정보 설정."""
        session = self.client.session
        session['user_id'] = user_info['user_id']
        session['user_name'] = user_info['user_name']
        session['user_compname'] = user_info['user_compname']
        session['user_deptname'] = user_info['user_deptname']
        session['is_admin'] = user_info['is_admin']
        session.save()

    def test_author_can_access_private_post(self):
        """작성자는 비밀글 접근 가능."""
        self._set_session(self.author_info)

        response = self.client.get(f'/support/api/posts/{self.private_post.id}/')

        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result['title'], '비밀글')
        self.assertNotIn('access_denied', result)

    def test_admin_can_access_private_post(self):
        """관리자는 비밀글 접근 가능."""
        self._set_session(self.admin_info)

        response = self.client.get(f'/support/api/posts/{self.private_post.id}/')

        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result['title'], '비밀글')
        self.assertNotIn('access_denied', result)

    def test_other_user_cannot_access_private_post(self):
        """타인은 비밀글 접근 불가 (access_denied 응답)."""
        self._set_session(self.other_user_info)

        response = self.client.get(f'/support/api/posts/{self.private_post.id}/')

        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertTrue(result.get('access_denied'))

    def test_anonymous_cannot_access_private_post(self):
        """비로그인 유저는 비밀글 접근 불가 (access_denied 응답)."""
        response = self.client.get(f'/support/api/posts/{self.private_post.id}/')

        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertTrue(result.get('access_denied'))

    def test_private_post_hidden_in_list(self):
        """비밀글은 목록에서 제목/내용 숨김."""
        response = self.client.get('/support/api/posts/')

        self.assertEqual(response.status_code, 200)
        result = response.json()
        post_data = result['posts'][0]
        self.assertEqual(post_data['title'], '비밀글입니다.')
        self.assertEqual(post_data['content'], '')


class CommentAPITest(TestCase):
    """댓글 API 테스트."""

    def setUp(self):
        """테스트 데이터 설정."""
        self.client = Client()

        # TODO: User factory를 사용하여 테스트 유저 생성
        # self.user = UserFactory(is_admin=False)
        # self.admin = UserFactory(is_admin=True)
        # self.other_user = UserFactory(is_admin=False)

        self.user_info = {
            'user_id': 'user-001',
            'user_name': 'testuser',
            'user_compname': '테스트회사',
            'user_deptname': '테스트부서',
            'is_admin': False,
        }
        self.admin_info = {
            'user_id': 'admin-001',
            'user_name': 'adminuser',
            'user_compname': '관리회사',
            'user_deptname': '관리부서',
            'is_admin': True,
        }
        self.other_user_info = {
            'user_id': 'other-001',
            'user_name': 'otheruser',
            'user_compname': '타회사',
            'user_deptname': '타부서',
            'is_admin': False,
        }

        self.public_post = Post.objects.create(
            title='공개글',
            content='내용',
            user_name='작성자',
        )
        self.private_post = Post.objects.create(
            title='비밀글',
            content='비밀 내용',
            user_name='작성자',
            user_id=self.user_info['user_id'],
            is_private=True,
        )

    def _set_session(self, user_info):
        """세션에 유저 정보 설정."""
        session = self.client.session
        session['user_id'] = user_info['user_id']
        session['user_name'] = user_info['user_name']
        session['user_compname'] = user_info['user_compname']
        session['user_deptname'] = user_info['user_deptname']
        session['is_admin'] = user_info['is_admin']
        session.save()

    def test_create_comment_on_public_post(self):
        """공개글에 댓글 작성 테스트."""
        data = {
            'content': '댓글 내용',
            'user_name': '댓글작성자',
        }

        response = self.client.post(
            f'/support/api/posts/{self.public_post.id}/comments/',
            json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)
        result = response.json()
        self.assertEqual(result['content'], '댓글 내용')

    def test_author_can_comment_on_private_post(self):
        """비밀글 작성자는 댓글 작성 가능."""
        self._set_session(self.user_info)

        data = {
            'content': '작성자 댓글',
            'user_name': '작성자',
        }

        response = self.client.post(
            f'/support/api/posts/{self.private_post.id}/comments/',
            json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)

    def test_admin_can_comment_on_private_post(self):
        """관리자는 비밀글에 댓글 작성 가능."""
        self._set_session(self.admin_info)

        data = {
            'content': '관리자 댓글',
            'user_name': '관리자',
        }

        response = self.client.post(
            f'/support/api/posts/{self.private_post.id}/comments/',
            json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)

    def test_other_user_cannot_comment_on_private_post(self):
        """타인은 비밀글에 댓글 작성 불가 (access_denied 응답)."""
        self._set_session(self.other_user_info)

        data = {
            'content': '타인 댓글',
            'user_name': '타인',
        }

        response = self.client.post(
            f'/support/api/posts/{self.private_post.id}/comments/',
            json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertTrue(result.get('access_denied'))

    def test_anonymous_cannot_comment_on_private_post(self):
        """비로그인 유저는 비밀글에 댓글 작성 불가 (access_denied 응답)."""
        data = {
            'content': '익명 댓글',
            'user_name': '익명',
        }

        response = self.client.post(
            f'/support/api/posts/{self.private_post.id}/comments/',
            json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertTrue(result.get('access_denied'))


class TagAPITest(TestCase):
    """태그 API 테스트."""

    def setUp(self):
        """테스트 데이터 설정."""
        self.client = Client()

    def test_list_tags(self):
        """태그 목록 조회 테스트."""
        Tag.objects.create(name='Django')
        Tag.objects.create(name='Python')
        Tag.objects.create(name='API')

        response = self.client.get('/support/api/tags/')

        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(len(result['tags']), 3)

    def test_tags_created_with_post(self):
        """게시글 생성 시 태그도 함께 생성."""
        data = {
            'title': '태그 테스트',
            'content': '내용',
            'user_name': '작성자',
            'tags': ['NewTag1', 'NewTag2'],
        }

        self.client.post(
            '/support/api/posts/create/',
            json.dumps(data),
            content_type='application/json'
        )

        self.assertTrue(Tag.objects.filter(name='NewTag1').exists())
        self.assertTrue(Tag.objects.filter(name='NewTag2').exists())


class ValidationTest(TestCase):
    """입력값 검증 테스트."""

    def test_xss_prevention(self):
        """XSS 방지 테스트."""
        from support_board.validators import ValidationService

        malicious_input = '<script>alert("xss")</script>'
        sanitized = ValidationService.sanitize_string(malicious_input, 200, 'test')

        self.assertNotIn('<script>', sanitized)
        self.assertIn('&lt;script&gt;', sanitized)

    def test_title_length_limit(self):
        """제목 길이 제한 테스트."""
        from support_board.validators import ValidationService, ValidationError

        long_title = 'a' * 201

        with self.assertRaises(ValidationError):
            ValidationService.sanitize_string(long_title, 200, '제목')

    def test_tags_count_limit(self):
        """태그 개수 제한 테스트."""
        from support_board.validators import ValidationService, ValidationError

        too_many_tags = ['tag' + str(i) for i in range(11)]

        with self.assertRaises(ValidationError):
            ValidationService.sanitize_tags(too_many_tags)

    def test_empty_title_validation(self):
        """빈 제목 검증 테스트."""
        from support_board.validators import ValidationService, ValidationError

        with self.assertRaises(ValidationError):
            ValidationService.sanitize_string('', 200, '제목')

    def test_empty_content_validation(self):
        """빈 내용 검증 테스트."""
        from support_board.validators import ValidationService, ValidationError

        with self.assertRaises(ValidationError):
            ValidationService.sanitize_string('   ', 10000, '내용')
