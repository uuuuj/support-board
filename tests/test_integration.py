"""통합 테스트.

WebSocket 서버 → API → DB 전체 흐름을 테스트합니다.
"""

import asyncio
import json
import uuid
import threading
import time
from unittest import TestCase as UnitTestCase

import websockets
from django.test import TestCase, Client

from support_board.models import User, Post


class TestResults:
    """테스트 결과 저장"""
    items = []

    @classmethod
    def add(cls, name, status):
        cls.items.append((name, status))

    @classmethod
    def print_summary(cls):
        print("\n" + "=" * 50)
        print("통합 테스트 결과 요약")
        print("=" * 50)
        for name, status in cls.items:
            icon = "PASS" if status == "PASS" else "FAIL"
            print(f"[{icon}] {name}")
        print("=" * 50)
        cls.items = []


class MockWebSocketServer:
    """테스트용 Mock WebSocket 서버."""

    def __init__(self, host='localhost', port=8766):
        self.host = host
        self.port = port
        self.server = None
        self.loop = None
        self.thread = None
        self.user_data = {
            'user_id': str(uuid.uuid4()),
            'username': '통합테스트유저',
            'is_admin': False,
        }

    async def handle_connection(self, websocket):
        """WebSocket 연결 처리."""
        async for message in websocket:
            data = json.loads(message)
            if data.get('type') == 'get_user_info':
                response = {
                    'type': 'user_info',
                    'status': 'success',
                    'data': self.user_data,
                }
                await websocket.send(json.dumps(response))

    async def start_server(self):
        """서버 시작."""
        self.server = await websockets.serve(
            self.handle_connection,
            self.host,
            self.port
        )
        await self.server.wait_closed()

    def start(self):
        """별도 스레드에서 서버 시작."""
        self.loop = asyncio.new_event_loop()

        def run():
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(self.start_server())

        self.thread = threading.Thread(target=run, daemon=True)
        self.thread.start()
        time.sleep(0.5)  # 서버 시작 대기

    def stop(self):
        """서버 중지."""
        if self.server:
            self.server.close()
        if self.loop:
            self.loop.call_soon_threadsafe(self.loop.stop)


class WebSocketClientTest(UnitTestCase):
    """WebSocket 클라이언트 테스트."""

    @classmethod
    def setUpClass(cls):
        """테스트 클래스 설정."""
        super().setUpClass()
        cls.ws_server = MockWebSocketServer(port=8766)
        cls.ws_server.start()

    @classmethod
    def tearDownClass(cls):
        """테스트 클래스 정리."""
        cls.ws_server.stop()
        super().tearDownClass()

    def test_websocket_connection(self):
        """WebSocket 연결 및 유저 정보 수신 테스트."""
        async def test():
            async with websockets.connect('ws://localhost:8766') as ws:
                await ws.send(json.dumps({'type': 'get_user_info'}))
                response = await ws.recv()
                data = json.loads(response)

                self.assertEqual(data['status'], 'success')
                self.assertEqual(data['data']['username'], '통합테스트유저')

        try:
            asyncio.get_event_loop().run_until_complete(test())
            TestResults.add("test_websocket_connection", "PASS")
        except AssertionError:
            TestResults.add("test_websocket_connection", "FAIL")
            raise


class IntegrationFlowTest(TestCase):
    """전체 통합 흐름 테스트."""

    def setUp(self):
        """테스트 설정."""
        self.client = Client()

    def test_full_flow_user_sync_to_private_post(self):
        """유저 동기화 → 비밀글 생성 전체 흐름."""
        user_data = {
            'user_id': str(uuid.uuid4()),
            'username': '통합테스트유저',
            'is_admin': False,
        }
        sync_response = self.client.post(
            '/support/api/users/sync/',
            json.dumps(user_data),
            content_type='application/json'
        )

        try:
            self.assertEqual(sync_response.status_code, 201)

            me_response = self.client.get('/support/api/users/me/')
            self.assertEqual(me_response.status_code, 200)
            result = me_response.json()
            self.assertEqual(result['username'], '통합테스트유저')

            post_data = {
                'title': '비밀글 테스트',
                'content': '비밀 내용입니다.',
                'author': '통합테스트유저',
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

            detail_response = self.client.get(f'/support/api/posts/{post_id}/')
            self.assertEqual(detail_response.status_code, 200)
            detail_result = detail_response.json()
            self.assertEqual(detail_result['title'], '비밀글 테스트')

            TestResults.add("test_full_flow_user_sync_to_private_post", "PASS")
        except AssertionError:
            TestResults.add("test_full_flow_user_sync_to_private_post", "FAIL")
            raise

    def test_other_user_cannot_access_private_post(self):
        """다른 유저는 비밀글 접근 불가."""
        user1_data = {
            'user_id': str(uuid.uuid4()),
            'username': '유저1',
            'is_admin': False,
        }
        self.client.post(
            '/support/api/users/sync/',
            json.dumps(user1_data),
            content_type='application/json'
        )

        post_data = {
            'title': '유저1의 비밀글',
            'content': '비밀 내용',
            'author': '유저1',
            'is_private': True,
        }
        post_response = self.client.post(
            '/support/api/posts/create/',
            json.dumps(post_data),
            content_type='application/json'
        )
        post_id = post_response.json()['id']

        new_client = Client()
        user2_data = {
            'user_id': str(uuid.uuid4()),
            'username': '유저2',
            'is_admin': False,
        }
        new_client.post(
            '/support/api/users/sync/',
            json.dumps(user2_data),
            content_type='application/json'
        )

        try:
            detail_response = new_client.get(f'/support/api/posts/{post_id}/')
            self.assertEqual(detail_response.status_code, 403)
            TestResults.add("test_other_user_cannot_access_private_post", "PASS")
        except AssertionError:
            TestResults.add("test_other_user_cannot_access_private_post", "FAIL")
            raise

    def test_admin_can_access_any_private_post(self):
        """관리자는 모든 비밀글 접근 가능."""
        user_data = {
            'user_id': str(uuid.uuid4()),
            'username': '일반유저',
            'is_admin': False,
        }
        self.client.post(
            '/support/api/users/sync/',
            json.dumps(user_data),
            content_type='application/json'
        )

        post_data = {
            'title': '일반유저의 비밀글',
            'content': '비밀 내용',
            'author': '일반유저',
            'is_private': True,
        }
        post_response = self.client.post(
            '/support/api/posts/create/',
            json.dumps(post_data),
            content_type='application/json'
        )
        post_id = post_response.json()['id']

        admin_client = Client()
        admin_data = {
            'user_id': str(uuid.uuid4()),
            'username': '관리자',
            'is_admin': True,
        }
        admin_client.post(
            '/support/api/users/sync/',
            json.dumps(admin_data),
            content_type='application/json'
        )

        try:
            detail_response = admin_client.get(f'/support/api/posts/{post_id}/')
            self.assertEqual(detail_response.status_code, 200)
            detail_result = detail_response.json()
            self.assertEqual(detail_result['title'], '일반유저의 비밀글')
            TestResults.add("test_admin_can_access_any_private_post", "PASS")
        except AssertionError:
            TestResults.add("test_admin_can_access_any_private_post", "FAIL")
            raise

    def test_admin_can_comment_on_private_post(self):
        """관리자는 타인의 비밀글에 댓글 작성 가능."""
        user_data = {
            'user_id': str(uuid.uuid4()),
            'username': '일반유저',
            'is_admin': False,
        }
        self.client.post(
            '/support/api/users/sync/',
            json.dumps(user_data),
            content_type='application/json'
        )

        post_data = {
            'title': '일반유저의 비밀글',
            'content': '비밀 내용',
            'author': '일반유저',
            'is_private': True,
        }
        post_response = self.client.post(
            '/support/api/posts/create/',
            json.dumps(post_data),
            content_type='application/json'
        )
        post_id = post_response.json()['id']

        admin_client = Client()
        admin_data = {
            'user_id': str(uuid.uuid4()),
            'username': '관리자',
            'is_admin': True,
        }
        admin_client.post(
            '/support/api/users/sync/',
            json.dumps(admin_data),
            content_type='application/json'
        )

        comment_data = {
            'content': '관리자 댓글입니다.',
            'author': '관리자',
        }

        try:
            comment_response = admin_client.post(
                f'/support/api/posts/{post_id}/comments/',
                json.dumps(comment_data),
                content_type='application/json'
            )
            self.assertEqual(comment_response.status_code, 201)
            TestResults.add("test_admin_can_comment_on_private_post", "PASS")
        except AssertionError:
            TestResults.add("test_admin_can_comment_on_private_post", "FAIL")
            raise

    @classmethod
    def tearDownClass(cls):
        """마지막 테스트 클래스 끝나면 요약 출력"""
        super().tearDownClass()
        TestResults.print_summary()
