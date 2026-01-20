/**
 * React 컴포넌트 테스트
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { PostCreate } from '../main';

// userSync mock
vi.mock('../userSync', () => ({
  startUserSyncPolling: vi.fn(() => () => {}),
  getCurrentUser: vi.fn(() => Promise.resolve(null)),
}));

describe('PostCreate 컴포넌트', () => {
  const mockOnBack = vi.fn();
  const mockOnSubmit = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('폼이 렌더링된다', () => {
    render(
      <PostCreate
        onBack={mockOnBack}
        onSubmit={mockOnSubmit}
        currentUser={null}
      />
    );

    expect(screen.getByPlaceholderText('제목을 입력하세요')).toBeInTheDocument();
    expect(screen.getByText('Create a new question')).toBeInTheDocument();
  });

  it('미로그인 시 비밀글 토글이 비활성화된다', () => {
    render(
      <PostCreate
        onBack={mockOnBack}
        onSubmit={mockOnSubmit}
        currentUser={null}
      />
    );

    expect(screen.getByText('(로그인 필요)')).toBeInTheDocument();
  });

  it('로그인 시 비밀글 토글이 활성화된다', () => {
    const currentUser = { uuid: 'test-uuid', username: '테스트유저', is_admin: false };

    render(
      <PostCreate
        onBack={mockOnBack}
        onSubmit={mockOnSubmit}
        currentUser={currentUser}
      />
    );

    expect(screen.queryByText('(로그인 필요)')).not.toBeInTheDocument();
  });

  it('뒤로가기 버튼 클릭 시 onBack이 호출된다', () => {
    render(
      <PostCreate
        onBack={mockOnBack}
        onSubmit={mockOnSubmit}
        currentUser={null}
      />
    );

    // ArrowLeft 아이콘이 있는 버튼 찾기
    const backButtons = screen.getAllByRole('button');
    const backButton = backButtons[0]; // 첫 번째 버튼이 뒤로가기

    fireEvent.click(backButton);

    expect(mockOnBack).toHaveBeenCalled();
  });

  it('필수 필드 미입력 시 alert가 표시된다', () => {
    const alertMock = vi.spyOn(window, 'alert').mockImplementation(() => {});

    render(
      <PostCreate
        onBack={mockOnBack}
        onSubmit={mockOnSubmit}
        currentUser={null}
      />
    );

    const submitButton = screen.getByText('Publish');
    fireEvent.click(submitButton);

    expect(alertMock).toHaveBeenCalledWith('제목과 내용을 모두 입력해주세요.');
    expect(mockOnSubmit).not.toHaveBeenCalled();

    alertMock.mockRestore();
  });

  it('모든 필드 입력 시 onSubmit이 호출된다', () => {
    render(
      <PostCreate
        onBack={mockOnBack}
        onSubmit={mockOnSubmit}
        currentUser={null}
      />
    );

    const titleInput = screen.getByPlaceholderText('제목을 입력하세요');
    const contentInput = screen.getByPlaceholderText('What are your thoughts?');

    fireEvent.change(titleInput, { target: { value: '테스트 제목' } });
    fireEvent.change(contentInput, { target: { value: '테스트 내용' } });

    const submitButton = screen.getByText('Publish');
    fireEvent.click(submitButton);

    expect(mockOnSubmit).toHaveBeenCalledWith(
      expect.objectContaining({
        title: '테스트 제목',
        content: '테스트 내용',
      })
    );
  });

  it('로그인 상태에서 비밀글 선택 후 제출 시 is_private이 true로 전송된다', async () => {
    const currentUser = { uuid: 'test-uuid', username: '테스트유저', is_admin: false };

    render(
      <PostCreate
        onBack={mockOnBack}
        onSubmit={mockOnSubmit}
        currentUser={currentUser}
      />
    );

    const titleInput = screen.getByPlaceholderText('제목을 입력하세요');
    const contentInput = screen.getByPlaceholderText('What are your thoughts?');

    fireEvent.change(titleInput, { target: { value: '비밀 제목' } });
    fireEvent.change(contentInput, { target: { value: '비밀 내용' } });

    // 비밀글 토글 클릭 (비밀글 텍스트 옆의 토글 버튼)
    const privateLabel = screen.getByText('비밀글');
    const toggleContainer = privateLabel.closest('div').parentElement;
    const toggleButton = toggleContainer.querySelector('button');

    fireEvent.click(toggleButton);

    const submitButton = screen.getByText('Publish');
    fireEvent.click(submitButton);

    expect(mockOnSubmit).toHaveBeenCalledWith(
      expect.objectContaining({
        is_private: true,
      })
    );
  });
});
