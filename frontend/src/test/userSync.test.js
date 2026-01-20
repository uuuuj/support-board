/**
 * userSync.js 테스트
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
  getCurrentUser,
} from '../userSync';

describe('userSync', () => {
  let originalFetch;

  beforeEach(() => {
    originalFetch = global.fetch;
  });

  afterEach(() => {
    global.fetch = originalFetch;
    vi.restoreAllMocks();
  });

  describe('getCurrentUser', () => {
    it('현재는 null을 반환한다 (세션 기반 인증 대기)', async () => {
      const result = await getCurrentUser();
      expect(result).toBeNull();
    });
  });
});
