"""
Mock WebSocket Server for Testing

실제 환경에서는 각 사용자 PC의 localhost에서 실행되는 서버가
유저 정보를 제공합니다. 이 파일은 테스트용 Mock 서버입니다.

실행: python mock_ws_server.py
포트: 8765
"""

import asyncio
import json
import uuid
import websockets

# 서버 시작 시 랜덤 UUID 생성 (세션 동안 유지)
USER_UUID = str(uuid.uuid4())

# 테스트용 더미 유저 데이터
DUMMY_USER = {
    "user_id": USER_UUID,
    "username": "테스트유저",
    "email": "test@example.com",
    "department": "개발팀",
    "is_admin": False,
}


async def handle_connection(websocket):
    """WebSocket 연결 처리."""
    print(f"클라이언트 연결됨: {websocket.remote_address}")

    try:
        async for message in websocket:
            data = json.loads(message)

            if data.get("type") == "get_user_info":
                # 유저 정보 요청에 응답
                response = {
                    "type": "user_info",
                    "data": DUMMY_USER,
                    "status": "success",
                }
                await websocket.send(json.dumps(response))
                print(f"유저 정보 전송: {DUMMY_USER['username']} ({DUMMY_USER['user_id']})")
            else:
                # 알 수 없는 요청
                response = {
                    "type": "error",
                    "message": "Unknown request type",
                    "status": "error",
                }
                await websocket.send(json.dumps(response))

    except websockets.exceptions.ConnectionClosed:
        print(f"클라이언트 연결 종료: {websocket.remote_address}")


async def main():
    """WebSocket 서버 시작."""
    port = 8765
    print(f"Mock WebSocket 서버 시작 - ws://localhost:{port}")
    print("테스트용 유저 정보:")
    print(json.dumps(DUMMY_USER, indent=2, ensure_ascii=False))
    print("-" * 50)

    async with websockets.serve(handle_connection, "localhost", port):
        await asyncio.Future()  # 서버 계속 실행


if __name__ == "__main__":
    asyncio.run(main())
