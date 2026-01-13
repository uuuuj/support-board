"""통합 테스트.

WebSocket 서버 → API → DB 전체 흐름을 테스트합니다.
"""

import asyncio
import json
import uuid
import threading
import time
from unittest import TestCase

import websockets
from django.test import LiveServerTestCase, override_settings
from rest_framework.test import APIClient

from support_board.models import User, Post


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


class WebSocketClientTest(TestCase):
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

        asyncio.get_event_loop().run_until_complete(test())


class IntegrationFlowTest(LiveServerTestCase):
    """전체 통합 흐름 테스트."""

    @classmethod
    def setUpClass(cls):
        """테스트 클래스 설정."""
        super().setUpClass()
        cls.ws_server = MockWebSocketServer(port=8767)
        cls.ws_server.start()

    @classmethod
    def tearDownClass(cls):
        """테스트 클래스 정리."""
        cls.ws_server.stop()
        super().tearDownClass()

    def setUp(self):
        """테스트 설정."""
        self.client = APIClient()

    def test_full_flow_websocket_to_private_post(self):
        """WebSocket → 유저 동기화 → 비밀글 생성 전체 흐름."""
        # 1. WebSocket에서 유저 정보 가져오기
        async def get_user_from_ws():
            async with websockets.connect('ws://localhost:8767') as ws:
                await ws.send(json.dumps({'type': 'get_user_info'}))
                response = await ws.recv()
                return json.loads(response)['data']

        user_data = asyncio.get_event_loop().run_until_complete(get_user_from_ws())

        # 2. Django API로 유저 동기화
        sync_response = self.client.post(
            '/support/api/users/sync/',
            user_data,
            format='json'
        )
        self.assertEqual(sync_response.status_code, 201)

        # 3. 세션 확인
        me_response = self.client.get('/support/api/users/me/')
        self.assertEqual(me_response.status_code, 200)
        self.assertEqual(me_response.data['username'], '통합테스트유저')

        # 4. 비밀글 생성
        post_data = {
            'title': '비밀글 테스트',
            'content': '비밀 내용입니다.',
            'author': '통합테스트유저',
            'is_private': True,
        }
        post_response = self.client.post(
            '/support/api/posts/create/',
            post_data,
            format='json'
        )
        self.assertEqual(post_response.status_code, 201)
        self.assertTrue(post_response.data['is_private'])

        post_id = post_response.data['id']

        # 5. 작성자가 비밀글 조회 가능
        detail_response = self.client.get(f'/support/api/posts/{post_id}/')
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(detail_response.data['title'], '비밀글 테스트')

    def test_other_user_cannot_access_private_post(self):
        """다른 유저는 비밀글 접근 불가."""
        # 1. 첫 번째 유저로 비밀글 생성
        user1_data = {
            'user_id': str(uuid.uuid4()),
            'username': '유저1',
            'is_admin': False,
        }
        self.client.post('/support/api/users/sync/', user1_data, format='json')

        post_data = {
            'title': '유저1의 비밀글',
            'content': '비밀 내용',
            'author': '유저1',
            'is_private': True,
        }
        post_response = self.client.post(
            '/support/api/posts/create/',
            post_data,
            format='json'
        )
        post_id = post_response.data['id']

        # 2. 다른 유저로 세션 변경
        new_client = APIClient()
        user2_data = {
            'user_id': str(uuid.uuid4()),
            'username': '유저2',
            'is_admin': False,
        }
        new_client.post('/support/api/users/sync/', user2_data, format='json')

        # 3. 다른 유저가 비밀글 접근 시도
        detail_response = new_client.get(f'/support/api/posts/{post_id}/')
        self.assertEqual(detail_response.status_code, 403)

    def test_admin_can_access_any_private_post(self):
        """관리자는 모든 비밀글 접근 가능."""
        # 1. 일반 유저로 비밀글 생성
        user_data = {
            'user_id': str(uuid.uuid4()),
            'username': '일반유저',
            'is_admin': False,
        }
        self.client.post('/support/api/users/sync/', user_data, format='json')

        post_data = {
            'title': '일반유저의 비밀글',
            'content': '비밀 내용',
            'author': '일반유저',
            'is_private': True,
        }
        post_response = self.client.post(
            '/support/api/posts/create/',
            post_data,
            format='json'
        )
        post_id = post_response.data['id']

        # 2. 관리자로 세션 변경
        admin_client = APIClient()
        admin_data = {
            'user_id': str(uuid.uuid4()),
            'username': '관리자',
            'is_admin': True,
        }
        admin_client.post('/support/api/users/sync/', admin_data, format='json')

        # 3. 관리자가 비밀글 접근
        detail_response = admin_client.get(f'/support/api/posts/{post_id}/')
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(detail_response.data['title'], '일반유저의 비밀글')

    def test_admin_can_comment_on_private_post(self):
        """관리자는 타인의 비밀글에 댓글 작성 가능."""
        # 1. 일반 유저로 비밀글 생성
        user_data = {
            'user_id': str(uuid.uuid4()),
            'username': '일반유저',
            'is_admin': False,
        }
        self.client.post('/support/api/users/sync/', user_data, format='json')

        post_data = {
            'title': '일반유저의 비밀글',
            'content': '비밀 내용',
            'author': '일반유저',
            'is_private': True,
        }
        post_response = self.client.post(
            '/support/api/posts/create/',
            post_data,
            format='json'
        )
        post_id = post_response.data['id']

        # 2. 관리자로 세션 변경
        admin_client = APIClient()
        admin_data = {
            'user_id': str(uuid.uuid4()),
            'username': '관리자',
            'is_admin': True,
        }
        admin_client.post('/support/api/users/sync/', admin_data, format='json')

        # 3. 관리자가 비밀글에 댓글 작성
        comment_data = {
            'content': '관리자 댓글입니다.',
            'author': '관리자',
        }
        comment_response = admin_client.post(
            f'/support/api/posts/{post_id}/comments/',
            comment_data,
            format='json'
        )
        self.assertEqual(comment_response.status_code, 201)
