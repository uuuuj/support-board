/**
 * WebSocket 기반 유저 동기화 모듈
 *
 * localhost WebSocket 서버에서 유저 정보를 가져와
 * Django 세션/DB에 동기화합니다.
 */

const WS_URL = 'ws://localhost:8765';
const API_BASE = '/support/api';
const POLLING_INTERVAL = 10 * 60 * 1000; // 10분

/**
 * WebSocket에서 유저 정보를 가져옵니다.
 * @returns {Promise<Object|null>} 유저 정보 또는 null
 */
async function fetchUserFromWebSocket() {
  return new Promise((resolve) => {
    try {
      const ws = new WebSocket(WS_URL);
      const timeout = setTimeout(() => {
        ws.close();
        resolve(null);
      }, 5000); // 5초 타임아웃

      ws.onopen = () => {
        ws.send(JSON.stringify({ type: 'get_user_info' }));
      };

      ws.onmessage = (event) => {
        clearTimeout(timeout);
        try {
          const response = JSON.parse(event.data);
          if (response.status === 'success' && response.data) {
            resolve(response.data);
          } else {
            resolve(null);
          }
        } catch {
          resolve(null);
        }
        ws.close();
      };

      ws.onerror = () => {
        clearTimeout(timeout);
        resolve(null);
      };

      ws.onclose = () => {
        clearTimeout(timeout);
      };
    } catch {
      resolve(null);
    }
  });
}

/**
 * 유저 정보를 Django API로 전송하여 세션/DB에 동기화합니다.
 * @param {Object} userData - 유저 정보
 * @returns {Promise<Object|null>} 동기화된 유저 정보 또는 null
 */
async function syncUserToServer(userData) {
  try {
    const response = await fetch(`${API_BASE}/users/sync/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: userData.user_id,
        username: userData.username,
        is_admin: userData.is_admin || false,
      }),
    });

    if (response.ok) {
      return await response.json();
    }
    return null;
  } catch {
    return null;
  }
}

/**
 * 현재 세션의 유저 정보를 가져옵니다.
 * @returns {Promise<Object|null>} 유저 정보 또는 null
 */
async function getCurrentUser() {
  try {
    const response = await fetch(`${API_BASE}/users/me/`);
    if (response.ok) {
      return await response.json();
    }
    return null;
  } catch {
    return null;
  }
}

/**
 * 유저 동기화를 실행합니다.
 * @param {Function} onUserChange - 유저 변경 시 호출되는 콜백
 * @returns {Promise<Object|null>} 동기화된 유저 정보 또는 null
 */
async function syncUser(onUserChange) {
  const userData = await fetchUserFromWebSocket();

  if (userData) {
    const syncedUser = await syncUserToServer(userData);
    if (syncedUser && onUserChange) {
      onUserChange(syncedUser);
    }
    return syncedUser;
  }

  return null;
}

/**
 * 유저 동기화 폴링을 시작합니다.
 * @param {Function} onUserChange - 유저 변경 시 호출되는 콜백
 * @returns {Function} 폴링 중지 함수
 */
function startUserSyncPolling(onUserChange) {
  // 즉시 첫 동기화 실행
  syncUser(onUserChange);

  // 10분마다 폴링
  const intervalId = setInterval(() => {
    syncUser(onUserChange);
  }, POLLING_INTERVAL);

  // 중지 함수 반환
  return () => {
    clearInterval(intervalId);
  };
}

export {
  fetchUserFromWebSocket,
  syncUserToServer,
  getCurrentUser,
  syncUser,
  startUserSyncPolling,
};
