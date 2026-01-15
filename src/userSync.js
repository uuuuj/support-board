/**
 * 유저 동기화 모듈
 *
 * 외부 프로젝트에서 세션에 유저 정보를 설정합니다.
 * 이 모듈은 세션 정보를 읽어오는 역할만 합니다.
 */

const API_BASE = '/support/api';
const POLLING_INTERVAL = 10 * 60 * 1000; // 10분

/**
 * 현재 세션의 유저 정보를 가져옵니다.
 * 세션 정보는 외부 프로젝트에서 설정됩니다.
 * @returns {Promise<Object|null>} 유저 정보 또는 null
 */
async function getCurrentUser() {
  // 외부 프로젝트에서 세션을 통해 유저 정보가 설정됨
  // 현재는 세션 쿠키를 통해 서버에서 유저 정보를 확인
  // 필요시 외부 프로젝트의 API를 호출하도록 수정
  return null;
}

/**
 * 유저 동기화 폴링을 시작합니다.
 * 외부 프로젝트에서 세션 정보가 변경될 수 있으므로 주기적으로 확인합니다.
 * @param {Function} onUserChange - 유저 변경 시 호출되는 콜백
 * @returns {Function} 폴링 중지 함수
 */
function startUserSyncPolling(onUserChange) {
  // 즉시 첫 확인 실행
  getCurrentUser().then(user => {
    if (user && onUserChange) {
      onUserChange(user);
    }
  });

  // 주기적으로 확인 (외부 프로젝트에서 세션 변경 감지용)
  const intervalId = setInterval(() => {
    getCurrentUser().then(user => {
      if (onUserChange) {
        onUserChange(user);
      }
    });
  }, POLLING_INTERVAL);

  // 중지 함수 반환
  return () => {
    clearInterval(intervalId);
  };
}

export {
  getCurrentUser,
  startUserSyncPolling,
};
