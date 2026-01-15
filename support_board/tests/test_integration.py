"""통합 테스트.

API → DB 전체 흐름을 테스트합니다.
Factory Boy + Django TestCase를 사용합니다.
"""

import json
from django.test import TestCase, Client

from support_board.models import Post, Comment


class IntegrationFlowTest(TestCase):
    """전체 통합 흐름 테스트."""

    def setUp(self):
        """테스트 설정."""
        self.client = Client()

        # TODO: User factory를 사용하여 테스트 유저 생성
        # self.user = UserFactory(is_admin=False)
        # self.admin = UserFactory(is_admin=True)

        self.user_info = {
            'user_id': 'user-001',
            'user_name': '통합테스트유저',
            'user_compname': '테스트회사',
            'user_deptname': '테스트부서',
            'is_admin': False,
        }
        self.admin_info = {
            'user_id': 'admin-001',
            'user_name': '관리자',
            'user_compname': '관리회사',
            'user_deptname': '관리부서',
            'is_admin': True,
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

    def test_full_flow_create_private_post(self):
        """로그인 → 비밀글 생성 → 조회 전체 흐름."""
        self._set_session(self.user_info)

        # 비밀글 생성
        post_data = {
            'title': '비밀글 테스트',
            'content': '비밀 내용입니다.',
            'user_name': '통합테스트유저',
            'is_private': True,
        }
        post_response = self.client.post(
            '/support/api/posts/create/',
            json.dumps(post_data),
            content_type='application/json'
        )
        self.assertEqual(post_response.status_code, 201)
        post_result = post_response.json()
        self.assertTrue(post_result['is_private'])

        post_id = post_result['id']

        # 작성자가 상세 조회
        detail_response = self.client.get(f'/support/api/posts/{post_id}/')
        self.assertEqual(detail_response.status_code, 200)
        detail_result = detail_response.json()
        self.assertEqual(detail_result['title'], '비밀글 테스트')
        self.assertNotIn('access_denied', detail_result)

    def test_other_user_cannot_access_private_post(self):
        """다른 유저는 비밀글 접근 불가."""
        # 유저1로 비밀글 생성
        self._set_session(self.user_info)

        post_data = {
            'title': '유저1의 비밀글',
            'content': '비밀 내용',
            'user_name': '유저1',
            'is_private': True,
        }
        post_response = self.client.post(
            '/support/api/posts/create/',
            json.dumps(post_data),
            content_type='application/json'
        )
        post_id = post_response.json()['id']

        # 새 클라이언트로 유저2 세션 설정
        new_client = Client()
        user2_info = {
            'user_id': 'user-002',
            'user_name': '유저2',
            'user_compname': '타회사',
            'user_deptname': '타부서',
            'is_admin': False,
        }
        session = new_client.session
        session['user_id'] = user2_info['user_id']
        session['user_name'] = user2_info['user_name']
        session['user_compname'] = user2_info['user_compname']
        session['user_deptname'] = user2_info['user_deptname']
        session['is_admin'] = user2_info['is_admin']
        session.save()

        # 유저2가 비밀글 접근 시도
        detail_response = new_client.get(f'/support/api/posts/{post_id}/')
        self.assertEqual(detail_response.status_code, 200)
        result = detail_response.json()
        self.assertTrue(result.get('access_denied'))

    def test_admin_can_access_any_private_post(self):
        """관리자는 모든 비밀글 접근 가능."""
        # 일반 유저로 비밀글 생성
        self._set_session(self.user_info)

        post_data = {
            'title': '일반유저의 비밀글',
            'content': '비밀 내용',
            'user_name': '일반유저',
            'is_private': True,
        }
        post_response = self.client.post(
            '/support/api/posts/create/',
            json.dumps(post_data),
            content_type='application/json'
        )
        post_id = post_response.json()['id']

        # 관리자 클라이언트로 접근
        admin_client = Client()
        session = admin_client.session
        session['user_id'] = self.admin_info['user_id']
        session['user_name'] = self.admin_info['user_name']
        session['user_compname'] = self.admin_info['user_compname']
        session['user_deptname'] = self.admin_info['user_deptname']
        session['is_admin'] = self.admin_info['is_admin']
        session.save()

        # 관리자가 비밀글 접근
        detail_response = admin_client.get(f'/support/api/posts/{post_id}/')
        self.assertEqual(detail_response.status_code, 200)
        detail_result = detail_response.json()
        self.assertEqual(detail_result['title'], '일반유저의 비밀글')
        self.assertNotIn('access_denied', detail_result)

    def test_admin_can_comment_on_private_post(self):
        """관리자는 타인의 비밀글에 댓글 작성 가능."""
        # 일반 유저로 비밀글 생성
        self._set_session(self.user_info)

        post_data = {
            'title': '일반유저의 비밀글',
            'content': '비밀 내용',
            'user_name': '일반유저',
            'is_private': True,
        }
        post_response = self.client.post(
            '/support/api/posts/create/',
            json.dumps(post_data),
            content_type='application/json'
        )
        post_id = post_response.json()['id']

        # 관리자 클라이언트
        admin_client = Client()
        session = admin_client.session
        session['user_id'] = self.admin_info['user_id']
        session['user_name'] = self.admin_info['user_name']
        session['user_compname'] = self.admin_info['user_compname']
        session['user_deptname'] = self.admin_info['user_deptname']
        session['is_admin'] = self.admin_info['is_admin']
        session.save()

        # 관리자가 댓글 작성
        comment_data = {
            'content': '관리자 댓글입니다.',
            'user_name': '관리자',
        }
        comment_response = admin_client.post(
            f'/support/api/posts/{post_id}/comments/',
            json.dumps(comment_data),
            content_type='application/json'
        )
        self.assertEqual(comment_response.status_code, 201)

    def test_post_update_flow(self):
        """게시글 생성 → 수정 → 조회 흐름."""
        self._set_session(self.user_info)

        # 게시글 생성
        post_data = {
            'title': '원본 제목',
            'content': '원본 내용',
            'user_name': '작성자',
            'tags': ['Django', 'Test'],
        }
        create_response = self.client.post(
            '/support/api/posts/create/',
            json.dumps(post_data),
            content_type='application/json'
        )
        self.assertEqual(create_response.status_code, 201)
        post_id = create_response.json()['id']

        # 게시글 수정
        update_data = {
            'title': '수정된 제목',
            'content': '수정된 내용',
            'is_resolved': True,
        }
        update_response = self.client.put(
            f'/support/api/posts/{post_id}/update/',
            json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(update_response.status_code, 200)

        # 수정된 내용 확인
        detail_response = self.client.get(f'/support/api/posts/{post_id}/')
        result = detail_response.json()
        self.assertEqual(result['title'], '수정된 제목')
        self.assertEqual(result['content'], '수정된 내용')
        self.assertTrue(result['is_resolved'])

    def test_comment_flow(self):
        """게시글 생성 → 댓글 작성 → 상세 조회 흐름."""
        # 게시글 생성
        post_data = {
            'title': '댓글 테스트 게시글',
            'content': '내용',
            'user_name': '작성자',
        }
        create_response = self.client.post(
            '/support/api/posts/create/',
            json.dumps(post_data),
            content_type='application/json'
        )
        post_id = create_response.json()['id']

        # 댓글 작성
        comment_data = {
            'content': '첫 번째 댓글',
            'user_name': '댓글작성자1',
        }
        self.client.post(
            f'/support/api/posts/{post_id}/comments/',
            json.dumps(comment_data),
            content_type='application/json'
        )

        comment_data2 = {
            'content': '두 번째 댓글',
            'user_name': '댓글작성자2',
        }
        self.client.post(
            f'/support/api/posts/{post_id}/comments/',
            json.dumps(comment_data2),
            content_type='application/json'
        )

        # 상세 조회하여 댓글 확인
        detail_response = self.client.get(f'/support/api/posts/{post_id}/')
        result = detail_response.json()
        self.assertEqual(result['comments_count'], 2)
        self.assertEqual(len(result['comments']), 2)

    def test_tag_search_flow(self):
        """태그 생성 → 검색 흐름."""
        # 태그가 있는 게시글 생성
        post_data1 = {
            'title': 'Django 게시글',
            'content': '내용',
            'user_name': '작성자',
            'tags': ['Django', 'Python'],
        }
        self.client.post(
            '/support/api/posts/create/',
            json.dumps(post_data1),
            content_type='application/json'
        )

        post_data2 = {
            'title': 'React 게시글',
            'content': '내용',
            'user_name': '작성자',
            'tags': ['React', 'JavaScript'],
        }
        self.client.post(
            '/support/api/posts/create/',
            json.dumps(post_data2),
            content_type='application/json'
        )

        # 태그로 검색
        search_response = self.client.get('/support/api/posts/', {'tag': 'Django'})
        result = search_response.json()
        self.assertEqual(result['count'], 1)
        self.assertEqual(result['posts'][0]['title'], 'Django 게시글')

    def test_delete_flow(self):
        """게시글 생성 → 삭제 → 목록 확인 흐름."""
        self._set_session(self.user_info)

        # 게시글 생성
        post_data = {
            'title': '삭제될 게시글',
            'content': '내용',
            'user_name': '작성자',
        }
        create_response = self.client.post(
            '/support/api/posts/create/',
            json.dumps(post_data),
            content_type='application/json'
        )
        post_id = create_response.json()['id']

        # 게시글 삭제
        delete_response = self.client.delete(f'/support/api/posts/{post_id}/delete/')
        self.assertEqual(delete_response.status_code, 200)

        # 삭제 확인
        self.assertFalse(Post.objects.filter(id=post_id).exists())
