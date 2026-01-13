/**
 * userSync.js 테스트
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
  fetchUserFromWebSocket,
  syncUserToServer,
  getCurrentUser,
} from '../userSync';

// WebSocket Mock
class MockWebSocket {
  constructor(url) {
    this.url = url;
    this.onopen = null;
    this.onmessage = null;
    this.onerror = null;
    this.onclose = null;

    // 연결 성공 시뮬레이션
    setTimeout(() => {
      if (this.onopen) this.onopen();
    }, 10);
  }

  send(data) {
    const parsed = JSON.parse(data);
    if (parsed.type === 'get_user_info') {
      setTimeout(() => {
        if (this.onmessage) {
          this.onmessage({
            data: JSON.stringify({
              type: 'user_info',
              status: 'success',
              data: {
                user_id: 'test-uuid-1234',
                username: '테스트유저',
                is_admin: false,
              },
            }),
          });
        }
      }, 10);
    }
  }

  close() {
    if (this.onclose) this.onclose();
  }
}

// 에러 발생 WebSocket Mock
class ErrorWebSocket {
  constructor() {
    setTimeout(() => {
      if (this.onerror) this.onerror(new Error('Connection failed'));
    }, 10);
  }

  send() {}
  close() {}
}

describe('userSync', () => {
  let originalWebSocket;
  let originalFetch;

  beforeEach(() => {
    originalWebSocket = global.WebSocket;
    originalFetch = global.fetch;
  });

  afterEach(() => {
    global.WebSocket = originalWebSocket;
    global.fetch = originalFetch;
    vi.restoreAllMocks();
  });

  describe('fetchUserFromWebSocket', () => {
    it('WebSocket에서 유저 정보를 성공적으로 가져온다', async () => {
      global.WebSocket = MockWebSocket;

      const result = await fetchUserFromWebSocket();

      expect(result).not.toBeNull();
      expect(result.user_id).toBe('test-uuid-1234');
      expect(result.username).toBe('테스트유저');
      expect(result.is_admin).toBe(false);
    });

    it('WebSocket 연결 실패 시 null을 반환한다', async () => {
      global.WebSocket = ErrorWebSocket;

      const result = await fetchUserFromWebSocket();

      expect(result).toBeNull();
    });
  });

  describe('syncUserToServer', () => {
    it('유저 정보를 서버에 동기화한다', async () => {
      const mockResponse = {
        uuid: 'test-uuid-1234',
        username: '테스트유저',
        is_admin: false,
      };

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      const userData = {
        user_id: 'test-uuid-1234',
        username: '테스트유저',
        is_admin: false,
      };

      const result = await syncUserToServer(userData);

      expect(result).toEqual(mockResponse);
      expect(global.fetch).toHaveBeenCalledWith(
        '/support/api/users/sync/',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        })
      );
    });

    it('서버 에러 시 null을 반환한다', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
      });

      const userData = {
        user_id: 'test-uuid-1234',
        username: '테스트유저',
      };

      const result = await syncUserToServer(userData);

      expect(result).toBeNull();
    });

    it('네트워크 에러 시 null을 반환한다', async () => {
      global.fetch = vi.fn().mockRejectedValue(new Error('Network error'));

      const userData = {
        user_id: 'test-uuid-1234',
        username: '테스트유저',
      };

      const result = await syncUserToServer(userData);

      expect(result).toBeNull();
    });
  });

  describe('getCurrentUser', () => {
    it('현재 세션의 유저 정보를 가져온다', async () => {
      const mockUser = {
        uuid: 'test-uuid-1234',
        username: '테스트유저',
        is_admin: false,
      };

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockUser),
      });

      const result = await getCurrentUser();

      expect(result).toEqual(mockUser);
      expect(global.fetch).toHaveBeenCalledWith('/support/api/users/me/');
    });

    it('미로그인 시 null을 반환한다', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 401,
      });

      const result = await getCurrentUser();

      expect(result).toBeNull();
    });
  });
});
