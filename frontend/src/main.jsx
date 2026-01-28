import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import { MessageSquare, ChevronLeft, ChevronRight, ArrowLeft, MoreHorizontal, Plus, X, Search, Filter, ChevronDown, Lock, Crown } from 'lucide-react';

// API 기본 URL (환경 변수에서 가져오거나 기본값 사용)
const API_BASE = import.meta.env.VITE_API_BASE || '/support/api';

// 현재 유저 정보 조회
const fetchCurrentUser = async () => {
  try {
    const response = await fetch(`${API_BASE}/user/`, {
      credentials: 'include',
    });
    const data = await response.json();
    if (data.is_authenticated) {
      return data.user;
    }
    return null;
  } catch (error) {
    console.error('Failed to fetch current user:', error);
    return null;
  }
};

// 게시글 작성 컴포넌트
const PostCreate = ({ onBack, onSubmit, currentUser }) => {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [isPrivate, setIsPrivate] = useState(false);
  const [tags, setTags] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!title.trim() || !content.trim()) {
      alert('제목과 내용을 모두 입력해주세요.');
      return;
    }
    if (isPrivate && !currentUser) {
      alert('비밀글 작성은 로그인이 필요합니다.');
      return;
    }
    onSubmit({
      title,
      content,
      is_private: isPrivate,
      tags: tags.split(',').map(t => t.trim()).filter(t => t),
    });
  };

  return (
    <div className="min-h-screen bg-gray-100 font-sans flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-sm max-w-2xl w-full p-8">
        {/* Header */}
        <div className="flex items-center gap-3 mb-8">
          <button
            onClick={onBack}
            className="p-1 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft size={20} className="text-gray-600" />
          </button>
          <h1 className="text-lg font-semibold text-gray-900">Create a new question</h1>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Title */}
          <div>
            <label className="block text-sm font-semibold text-gray-900 mb-2">
              Title
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="제목을 입력하세요"
              className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
            />
          </div>

          {/* Content */}
          <div>
            <label className="block text-sm font-semibold text-gray-900 mb-2">
              Content
            </label>
            <div className="border border-gray-200 rounded-lg overflow-hidden">
              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="What are your thoughts?"
                rows={8}
                className="w-full px-4 py-3 focus:outline-none resize-none"
              />
              {/* Toolbar */}
              <div className="flex items-center gap-1 px-3 py-2 border-t border-gray-100">
                <button type="button" className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                  <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </button>
                <button type="button" className="p-2 hover:bg-gray-100 rounded-lg transition-colors text-gray-500 font-semibold text-sm">
                  Aa
                </button>
                <button type="button" className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                  <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <circle cx="12" cy="12" r="10" strokeWidth={2} />
                    <path strokeLinecap="round" strokeWidth={2} d="M8 14s1.5 2 4 2 4-2 4-2" />
                    <circle cx="9" cy="9" r="1" fill="currentColor" />
                    <circle cx="15" cy="9" r="1" fill="currentColor" />
                  </svg>
                </button>
                <button type="button" className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                  <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <rect x="3" y="3" width="18" height="18" rx="2" strokeWidth={2} />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 15l5-5 4 4 5-5 4 4" />
                  </svg>
                </button>
                <button type="button" className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                  <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                  </svg>
                </button>
              </div>
            </div>
          </div>

          {/* Private Toggle */}
          <div className="flex items-center justify-between py-2">
            <div className="flex items-center gap-2">
              <Lock size={16} className="text-gray-500" />
              <span className="text-sm font-semibold text-gray-900">비밀글</span>
              {!currentUser && (
                <span className="text-xs text-gray-400">(로그인 필요)</span>
              )}
            </div>
            <button
              type="button"
              onClick={() => currentUser && setIsPrivate(!isPrivate)}
              disabled={!currentUser}
              className={`relative w-12 h-7 rounded-full transition-colors ${isPrivate ? 'bg-emerald-500' : 'bg-gray-200'} ${!currentUser ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
            >
              <span className={`absolute top-1 left-1 w-5 h-5 bg-white rounded-full shadow-sm transition-transform pointer-events-none ${isPrivate ? 'translate-x-5' : 'translate-x-0'}`} />
            </button>
          </div>

          {/* Tags */}
          <div>
            <label className="block text-sm font-semibold text-gray-900 mb-2">
              Tags
            </label>
            <div className="relative">
              <input
                type="text"
                value={tags}
                onChange={(e) => setTags(e.target.value)}
                placeholder="Add tags..."
                className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent pr-10"
              />
              <ChevronRight size={18} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 rotate-90" />
            </div>
          </div>

          {/* Buttons */}
          <div className="flex items-center justify-end gap-3 pt-4">
            <button
              type="button"
              onClick={onBack}
              className="px-6 py-2.5 border border-gray-200 rounded-full text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-6 py-2.5 bg-emerald-500 hover:bg-emerald-600 text-white rounded-full text-sm font-medium transition-colors"
            >
              Publish
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// 날짜 포맷 함수
const formatDate = (dateString) => {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now - date;
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays === 0) return 'Today';
  if (diffDays === 1) return 'Yesterday';
  if (diffDays < 7) return `${diffDays} days ago`;
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
  return `${Math.floor(diffDays / 30)} months ago`;
};

// 상세페이지 컴포넌트
const PostDetail = ({ post, onBack, onCommentSubmit, onCommentUpdate, onCommentDelete, onEdit, onDelete, currentUser }) => {
  const [commentText, setCommentText] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [replyingTo, setReplyingTo] = useState(null); // { id, user_name, isReply }
  const [showMenu, setShowMenu] = useState(false);
  const [showCommentMenu, setShowCommentMenu] = useState(null); // comment id
  const [editingComment, setEditingComment] = useState(null); // { id, content, isReply }
  const [editText, setEditText] = useState('');

  const handleSubmitComment = async (parentId = null) => {
    if (!commentText.trim() || submitting) return;

    setSubmitting(true);
    const success = await onCommentSubmit(commentText, parentId);
    if (success) {
      setCommentText('');
      setReplyingTo(null);
    }
    setSubmitting(false);
  };

  const handleKeyDown = (e, parentId = null) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmitComment(parentId);
    }
    if (e.key === 'Escape') {
      setReplyingTo(null);
      setCommentText('');
    }
  };

  const handleReplyClick = (comment, isReply = false) => {
    setReplyingTo({ id: comment.id, user_name: comment.user_name, isReply });
    setCommentText(isReply ? `@${comment.user_name} ` : '');
  };

  // 댓글 수정/삭제 권한 확인
  const canEditOrDeleteComment = (comment) => {
    return currentUser && (currentUser.is_admin || currentUser.user_id === comment.user_id);
  };

  // 댓글 수정 시작
  const handleEditCommentStart = (comment, isReply = false) => {
    setEditingComment({ id: comment.id, isReply });
    setEditText(comment.content);
    setShowCommentMenu(null);
  };

  // 댓글 수정 제출
  const handleEditCommentSubmit = async (commentId) => {
    if (!editText.trim() || submitting) return;
    setSubmitting(true);
    const success = await onCommentUpdate(commentId, editText);
    if (success) {
      setEditingComment(null);
      setEditText('');
    }
    setSubmitting(false);
  };

  // 댓글 삭제
  const handleDeleteComment = async (commentId) => {
    if (confirm('정말 삭제하시겠습니까?')) {
      setShowCommentMenu(null);
      await onCommentDelete(commentId);
    }
  };

  // 수정/삭제 권한 확인 (작성자 본인 또는 관리자)
  const canEditOrDelete = currentUser && (
    currentUser.is_admin || currentUser.user_id === post.user_id
  );

  const handleEdit = () => {
    setShowMenu(false);
    if (onEdit) onEdit(post);
  };

  const handleDelete = () => {
    setShowMenu(false);
    if (confirm('정말 삭제하시겠습니까?')) {
      if (onDelete) onDelete(post.id);
    }
  };

  // 총 댓글 수 계산 (원댓글 + 대댓글)
  const totalComments = (post.comments || []).reduce((acc, comment) => {
    return acc + 1 + (comment.replies?.length || 0);
  }, 0);

  return (
    <div className="min-h-screen bg-white font-sans">
      {/* Header */}
      <div className="sticky top-0 bg-white border-b border-gray-100 px-6 py-4 z-10">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={onBack}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <ArrowLeft size={20} className="text-gray-600" />
            </button>
            <span className="font-semibold text-gray-900">게시글</span>
          </div>
          <div className="relative">
            <button
              onClick={() => setShowMenu(!showMenu)}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <MoreHorizontal size={20} className="text-gray-600" />
            </button>
            {showMenu && (
              <div className="absolute right-0 top-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-20 min-w-[120px]">
                {canEditOrDelete ? (
                  <>
                    <button
                      onClick={handleEdit}
                      className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 first:rounded-t-lg"
                    >
                      수정하기
                    </button>
                    <button
                      onClick={handleDelete}
                      className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-50 last:rounded-b-lg"
                    >
                      삭제하기
                    </button>
                  </>
                ) : (
                  <div className="px-4 py-2 text-sm text-gray-400">
                    권한이 없습니다
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-6 py-8">
        {/* Author Info */}
        <div className="flex items-center gap-3 mb-6">
          <div className="w-12 h-12 bg-gray-300 rounded-full flex items-center justify-center flex-shrink-0">
            <span className="text-gray-600 font-medium text-lg">
              {post.user_name?.charAt(0)?.toUpperCase() || '?'}
            </span>
          </div>
          <div className="flex flex-col">
            <div className="flex items-center gap-2">
              <span className="font-semibold text-gray-900">{post.user_name || 'Anonymous'}</span>
              <span className="text-sm text-gray-400">·</span>
              <span className="text-sm text-gray-500">{post.date}</span>
            </div>
            <p className="text-sm text-gray-500 font-normal">{post.user_deptname || ''}</p>
          </div>
        </div>

        {/* Title */}
        <h1 className="text-2xl font-bold text-gray-900 mb-6">
          {post.title}
        </h1>

        {/* Body */}
        <div className="prose prose-gray max-w-none">
          <p className="text-gray-700 leading-relaxed mb-6 whitespace-pre-line">
            {post.content}
          </p>
        </div>

        {/* Tags */}
        {post.tags && post.tags.length > 0 && (
          <div className="flex items-start gap-4 mt-6 pt-6 border-t border-gray-100">
            <span className="text-sm font-medium text-gray-500 pt-1">Tag</span>
            <div className="flex flex-wrap gap-2">
              {post.tags.map((tag, idx) => (
                <span
                  key={idx}
                  className="px-4 py-1.5 border border-gray-200 rounded-full text-sm text-gray-600"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Comments Section */}
        <div className="mt-10">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-gray-900">Comments ({totalComments})</h2>
          </div>

          <div className="space-y-6">
            {post.comments && post.comments.length > 0 ? (
              post.comments.map((comment) => (
                <div key={comment.id}>
                  {/* 원댓글 */}
                  <div className="flex gap-3">
                    <div className="w-10 h-10 bg-gray-300 rounded-full flex items-center justify-center flex-shrink-0">
                      <span className="text-gray-600 font-medium text-sm">
                        {comment.is_deleted ? '?' : comment.user_name?.charAt(0)?.toUpperCase() || '?'}
                      </span>
                    </div>
                    <div className="flex-1">
                      <div className="flex items-start justify-between">
                        <div className="flex flex-col">
                          <div className="flex items-center gap-2">
                            <span className="font-semibold text-gray-900">
                              {comment.is_deleted ? '알 수 없음' : (comment.user_name || 'Anonymous')}
                            </span>
                            {!comment.is_deleted && comment.is_admin && (
                              <Crown size={14} className="text-yellow-500" title="관리자" />
                            )}
                            <span className="text-sm text-gray-400">·</span>
                            <span className="text-sm text-gray-500">{formatDate(comment.created_at)}</span>
                          </div>
                          {!comment.is_deleted && (
                            <p className="text-xs text-gray-500 font-normal">{comment.user_deptname || ''}</p>
                          )}
                        </div>
                        {!comment.is_deleted && (
                          <div className="relative">
                            <button
                              onClick={() => setShowCommentMenu(showCommentMenu === comment.id ? null : comment.id)}
                              className="p-1 hover:bg-gray-100 rounded transition-colors"
                            >
                              <MoreHorizontal size={16} className="text-gray-400" />
                            </button>
                            {showCommentMenu === comment.id && (
                              <div className="absolute right-0 top-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-20 min-w-[100px]">
                                {canEditOrDeleteComment(comment) ? (
                                  <>
                                    <button
                                      onClick={() => handleEditCommentStart(comment, false)}
                                      className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 first:rounded-t-lg"
                                    >
                                      수정
                                    </button>
                                    <button
                                      onClick={() => handleDeleteComment(comment.id)}
                                      className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-50 last:rounded-b-lg"
                                    >
                                      삭제
                                    </button>
                                  </>
                                ) : (
                                  <div className="px-4 py-2 text-sm text-gray-400">
                                    권한 없음
                                  </div>
                                )}
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                      {comment.is_deleted ? (
                        <div className="mt-2 text-gray-400 italic">
                          삭제된 댓글입니다.
                        </div>
                      ) : editingComment && editingComment.id === comment.id && !editingComment.isReply ? (
                        <div className="mt-2 flex items-center gap-2">
                          <input
                            type="text"
                            value={editText}
                            onChange={(e) => setEditText(e.target.value)}
                            className="flex-1 bg-gray-100 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                            disabled={submitting}
                            autoFocus
                          />
                          <button
                            onClick={() => handleEditCommentSubmit(comment.id)}
                            disabled={!editText.trim() || submitting}
                            className="px-3 py-2 bg-emerald-500 hover:bg-emerald-600 disabled:bg-gray-300 text-white rounded-lg text-sm font-medium transition-colors"
                          >
                            저장
                          </button>
                          <button
                            onClick={() => { setEditingComment(null); setEditText(''); }}
                            className="px-3 py-2 text-gray-500 hover:text-gray-700 text-sm"
                          >
                            취소
                          </button>
                        </div>
                      ) : (
                        <>
                          <div className="mt-2 text-gray-700 whitespace-pre-line leading-relaxed">
                            {comment.content}
                          </div>
                          {comment.is_edited && (
                            <span className="text-xs text-gray-400 mt-1 inline-block">수정됨</span>
                          )}
                        </>
                      )}
                      {!comment.is_deleted && !editingComment && (
                        <button
                          onClick={() => handleReplyClick(comment, false)}
                          className="mt-2 text-sm text-gray-500 hover:text-gray-700 block"
                        >
                          답글
                        </button>
                      )}
                    </div>
                  </div>

                  {/* 대댓글 목록 */}
                  {comment.replies && comment.replies.length > 0 && (
                    <div className="ml-12 mt-4 space-y-4">
                      {comment.replies.map((reply) => (
                        <div key={reply.id} className="flex gap-3">
                          <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center flex-shrink-0">
                            <span className="text-gray-500 font-medium text-xs">
                              {reply.is_deleted ? '?' : reply.user_name?.charAt(0)?.toUpperCase() || '?'}
                            </span>
                          </div>
                          <div className="flex-1">
                            <div className="flex items-start justify-between">
                              <div className="flex flex-col">
                                <div className="flex items-center gap-2">
                                  <span className="font-semibold text-gray-900 text-sm">
                                    {reply.is_deleted ? '알 수 없음' : (reply.user_name || 'Anonymous')}
                                  </span>
                                  {!reply.is_deleted && reply.is_admin && (
                                    <Crown size={12} className="text-yellow-500" title="관리자" />
                                  )}
                                  <span className="text-xs text-gray-400">·</span>
                                  <span className="text-xs text-gray-500">{formatDate(reply.created_at)}</span>
                                </div>
                                {!reply.is_deleted && (
                                  <p className="text-xs text-gray-500 font-normal">{reply.user_deptname || ''}</p>
                                )}
                              </div>
                              {!reply.is_deleted && (
                                <div className="relative">
                                  <button
                                    onClick={() => setShowCommentMenu(showCommentMenu === `reply-${reply.id}` ? null : `reply-${reply.id}`)}
                                    className="p-1 hover:bg-gray-100 rounded transition-colors"
                                  >
                                    <MoreHorizontal size={14} className="text-gray-400" />
                                  </button>
                                  {showCommentMenu === `reply-${reply.id}` && (
                                    <div className="absolute right-0 top-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-20 min-w-[100px]">
                                      {canEditOrDeleteComment(reply) ? (
                                        <>
                                          <button
                                            onClick={() => handleEditCommentStart(reply, true)}
                                            className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 first:rounded-t-lg"
                                          >
                                            수정
                                          </button>
                                          <button
                                            onClick={() => handleDeleteComment(reply.id)}
                                            className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-50 last:rounded-b-lg"
                                          >
                                            삭제
                                          </button>
                                        </>
                                      ) : (
                                        <div className="px-4 py-2 text-sm text-gray-400">
                                          권한 없음
                                        </div>
                                      )}
                                    </div>
                                  )}
                                </div>
                              )}
                            </div>
                            {reply.is_deleted ? (
                              <div className="mt-1 text-gray-400 italic text-sm">
                                삭제된 댓글입니다.
                              </div>
                            ) : editingComment && editingComment.id === reply.id && editingComment.isReply ? (
                              <div className="mt-1 flex items-center gap-2">
                                <input
                                  type="text"
                                  value={editText}
                                  onChange={(e) => setEditText(e.target.value)}
                                  className="flex-1 bg-gray-100 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                                  disabled={submitting}
                                  autoFocus
                                />
                                <button
                                  onClick={() => handleEditCommentSubmit(reply.id)}
                                  disabled={!editText.trim() || submitting}
                                  className="px-3 py-1.5 bg-emerald-500 hover:bg-emerald-600 disabled:bg-gray-300 text-white rounded-lg text-xs font-medium transition-colors"
                                >
                                  저장
                                </button>
                                <button
                                  onClick={() => { setEditingComment(null); setEditText(''); }}
                                  className="px-3 py-1.5 text-gray-500 hover:text-gray-700 text-xs"
                                >
                                  취소
                                </button>
                              </div>
                            ) : (
                              <>
                                <div className="mt-1 text-gray-700 text-sm whitespace-pre-line leading-relaxed">
                                  {reply.content}
                                </div>
                                {reply.is_edited && (
                                  <span className="text-xs text-gray-400 mt-0.5 inline-block">수정됨</span>
                                )}
                              </>
                            )}
                            {!reply.is_deleted && !editingComment && (
                              <button
                                onClick={() => handleReplyClick(reply, true)}
                                className="mt-1 text-xs text-gray-500 hover:text-gray-700 block"
                              >
                                답글
                              </button>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* 이 댓글에 답글 입력 중 */}
                  {replyingTo && replyingTo.id === comment.id && !replyingTo.isReply && (
                    <div className="ml-12 mt-4 flex items-center gap-2">
                      <input
                        type="text"
                        value={commentText}
                        onChange={(e) => setCommentText(e.target.value)}
                        onKeyDown={(e) => handleKeyDown(e, comment.id)}
                        placeholder={`${comment.user_name}님에게 답글...`}
                        className="flex-1 bg-gray-100 rounded-full px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                        disabled={submitting}
                        autoFocus
                      />
                      <button
                        onClick={() => handleSubmitComment(comment.id)}
                        disabled={!commentText.trim() || submitting}
                        className="px-3 py-2 bg-emerald-500 hover:bg-emerald-600 disabled:bg-gray-300 disabled:cursor-not-allowed text-white rounded-full text-sm font-medium transition-colors"
                      >
                        등록
                      </button>
                      <button
                        onClick={() => { setReplyingTo(null); setCommentText(''); }}
                        className="px-3 py-2 text-gray-500 hover:text-gray-700 text-sm"
                      >
                        취소
                      </button>
                    </div>
                  )}

                  {/* 대댓글에 답글 입력 중 (같은 원댓글 아래에 표시) */}
                  {replyingTo && replyingTo.isReply && comment.replies?.some(r => r.id === replyingTo.id) && (
                    <div className="ml-12 mt-4 flex items-center gap-2">
                      <input
                        type="text"
                        value={commentText}
                        onChange={(e) => setCommentText(e.target.value)}
                        onKeyDown={(e) => handleKeyDown(e, comment.id)}
                        placeholder={`${replyingTo.user_name}님에게 답글...`}
                        className="flex-1 bg-gray-100 rounded-full px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                        disabled={submitting}
                        autoFocus
                      />
                      <button
                        onClick={() => handleSubmitComment(comment.id)}
                        disabled={!commentText.trim() || submitting}
                        className="px-3 py-2 bg-emerald-500 hover:bg-emerald-600 disabled:bg-gray-300 disabled:cursor-not-allowed text-white rounded-full text-sm font-medium transition-colors"
                      >
                        등록
                      </button>
                      <button
                        onClick={() => { setReplyingTo(null); setCommentText(''); }}
                        className="px-3 py-2 text-gray-500 hover:text-gray-700 text-sm"
                      >
                        취소
                      </button>
                    </div>
                  )}
                </div>
              ))
            ) : (
              <p className="text-gray-500 text-center py-8">아직 댓글이 없습니다.</p>
            )}
          </div>
        </div>
      </div>

      {/* Comment Input (새 댓글) */}
      <div className="sticky bottom-0 bg-white border-t border-gray-200 px-6 py-4">
        <div className="max-w-4xl mx-auto flex items-center gap-2">
          <input
            type="text"
            value={replyingTo ? '' : commentText}
            onChange={(e) => !replyingTo && setCommentText(e.target.value)}
            onKeyDown={(e) => !replyingTo && handleKeyDown(e)}
            placeholder={replyingTo ? "위에서 답글을 작성하세요..." : "댓글을 입력하세요..."}
            className="flex-1 bg-gray-100 rounded-full px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
            disabled={submitting || replyingTo}
          />
          <button
            onClick={() => handleSubmitComment()}
            disabled={!commentText.trim() || submitting || replyingTo}
            className="px-4 py-2.5 bg-emerald-500 hover:bg-emerald-600 disabled:bg-gray-300 disabled:cursor-not-allowed text-white rounded-full text-sm font-medium transition-colors"
          >
            {submitting ? '등록 중...' : '등록'}
          </button>
        </div>
      </div>
    </div>
  );
};

const BoardList = () => {
  // 1. 상태 관리: 현재 페이지, 선택된 포스트, 작성 모드
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedPost, setSelectedPost] = useState(null);
  const [isCreating, setIsCreating] = useState(false);
  const [loading, setLoading] = useState(true);
  const itemsPerPage = 9;

  // 유저 상태
  const [currentUser, setCurrentUser] = useState(null);

  // 검색 상태
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('all'); // all, title, content, author, tag
  const [showFilterDropdown, setShowFilterDropdown] = useState(false);

  // 게시글 상태
  const [posts, setPosts] = useState([]);

  // API에서 게시글 목록 가져오기
  const fetchPosts = async (query = '', filter = 'all') => {
    setLoading(true);
    try {
      let url = `${API_BASE}/posts/`;
      const params = new URLSearchParams();

      if (query) {
        if (filter === 'all') {
          params.append('q', query);
        } else {
          params.append(filter, query);
        }
      }

      if (params.toString()) {
        url += `?${params.toString()}`;
      }

      const response = await fetch(url, {
        credentials: 'include',
      });
      const data = await response.json();

      // API 응답을 프론트엔드 형식으로 변환
      const formattedPosts = data.posts.map(post => ({
        ...post,
        date: formatDate(post.created_at),
        comments: post.comments_count || 0,
      }));

      setPosts(formattedPosts);
    } catch (error) {
      console.error('Failed to fetch posts:', error);
    } finally {
      setLoading(false);
    }
  };

  // 컴포넌트 마운트 시 게시글 가져오기 및 유저 정보 조회
  useEffect(() => {
    fetchPosts();

    // 현재 유저 정보 조회
    fetchCurrentUser().then(user => {
      setCurrentUser(user);
    });
  }, []);

  // 검색 실행 (디바운스 적용)
  useEffect(() => {
    const timer = setTimeout(() => {
      fetchPosts(searchQuery, filterType);
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery, filterType]);

  const filterOptions = [
    { value: 'all', label: '전체' },
    { value: 'title', label: '제목' },
    { value: 'content', label: '내용' },
    { value: 'user_name', label: '작성자' },
    { value: 'tag', label: '태그' },
  ];

  // CSRF 토큰 가져오기
  const getCsrfToken = () => {
    return document.cookie.split('; ')
      .find(row => row.startsWith('csrftoken='))?.split('=')[1];
  };

  // 새 게시글 작성 핸들러
  const handleCreatePost = async (newPost) => {
    try {
      const response = await fetch(`${API_BASE}/posts/create/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken(),
        },
        credentials: 'include',
        body: JSON.stringify({
          title: newPost.title,
          content: newPost.content,
          tags: newPost.tags || [],
          is_private: newPost.is_private || false,
        }),
      });

      if (response.ok) {
        // 게시글 목록 새로고침
        fetchPosts(searchQuery, filterType);
        setIsCreating(false);
      } else {
        alert('게시글 작성에 실패했습니다.');
      }
    } catch (error) {
      console.error('Failed to create post:', error);
      alert('게시글 작성에 실패했습니다.');
    }
  };

  // 댓글 작성 핸들러
  const handleCommentSubmit = async (content, parentId = null) => {
    if (!selectedPost) return false;

    try {
      const response = await fetch(`${API_BASE}/posts/${selectedPost.id}/comments/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken(),
        },
        credentials: 'include',
        body: JSON.stringify({ content, parent_id: parentId }),
      });

      if (response.ok) {
        const newComment = await response.json();

        if (parentId) {
          // 대댓글인 경우: 해당 부모 댓글의 replies에 추가
          setSelectedPost(prev => ({
            ...prev,
            comments: prev.comments.map(comment => {
              if (comment.id === parentId) {
                return {
                  ...comment,
                  replies: [...(comment.replies || []), newComment],
                };
              }
              return comment;
            }),
          }));
        } else {
          // 원댓글인 경우: comments 배열에 추가
          setSelectedPost(prev => ({
            ...prev,
            comments: [...(prev.comments || []), { ...newComment, replies: [] }],
          }));
        }
        return true;
      } else {
        alert('댓글 작성에 실패했습니다.');
        return false;
      }
    } catch (error) {
      console.error('Failed to create comment:', error);
      alert('댓글 작성에 실패했습니다.');
      return false;
    }
  };

  // 댓글 수정 핸들러
  const handleCommentUpdate = async (commentId, content) => {
    try {
      const response = await fetch(`${API_BASE}/comments/${commentId}/update/`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken(),
        },
        credentials: 'include',
        body: JSON.stringify({ content }),
      });

      const data = await response.json();
      if (data.access_denied) {
        alert(data.message || '수정 권한이 없습니다.');
        return false;
      }

      if (response.ok) {
        // 댓글 목록 업데이트
        setSelectedPost(prev => ({
          ...prev,
          comments: prev.comments.map(comment => {
            if (comment.id === commentId) {
              return { ...comment, content, is_edited: true };
            }
            // 대댓글에서도 찾기
            if (comment.replies) {
              return {
                ...comment,
                replies: comment.replies.map(reply =>
                  reply.id === commentId ? { ...reply, content, is_edited: true } : reply
                ),
              };
            }
            return comment;
          }),
        }));
        return true;
      }
      return false;
    } catch (error) {
      console.error('Failed to update comment:', error);
      alert('댓글 수정에 실패했습니다.');
      return false;
    }
  };

  // 댓글 삭제 핸들러
  const handleCommentDelete = async (commentId) => {
    try {
      const response = await fetch(`${API_BASE}/comments/${commentId}/delete/`, {
        method: 'DELETE',
        headers: {
          'X-CSRFToken': getCsrfToken(),
        },
        credentials: 'include',
      });

      const data = await response.json();
      if (data.access_denied) {
        alert(data.message || '삭제 권한이 없습니다.');
        return false;
      }

      if (response.ok) {
        // 댓글 목록 업데이트 (소프트 삭제 처리)
        setSelectedPost(prev => ({
          ...prev,
          comments: prev.comments.map(comment => {
            if (comment.id === commentId) {
              return { ...comment, is_deleted: true, content: '' };
            }
            // 대댓글에서도 찾기
            if (comment.replies) {
              return {
                ...comment,
                replies: comment.replies.map(reply =>
                  reply.id === commentId ? { ...reply, is_deleted: true, content: '' } : reply
                ),
              };
            }
            return comment;
          }),
        }));
        return true;
      }
      return false;
    } catch (error) {
      console.error('Failed to delete comment:', error);
      alert('댓글 삭제에 실패했습니다.');
      return false;
    }
  };

  // 게시글 삭제 핸들러
  const handleDeletePost = async (postId) => {
    try {
      const response = await fetch(`${API_BASE}/posts/${postId}/delete/`, {
        method: 'DELETE',
        headers: {
          'X-CSRFToken': getCsrfToken(),
        },
        credentials: 'include',
      });

      if (response.ok) {
        setSelectedPost(null);
        fetchPosts(searchQuery, filterType);
        alert('게시글이 삭제되었습니다.');
      } else {
        const data = await response.json();
        alert(data.message || '삭제 권한이 없습니다.');
      }
    } catch (error) {
      console.error('Failed to delete post:', error);
      alert('게시글 삭제에 실패했습니다.');
    }
  };

  // 게시글 수정 핸들러 (수정 페이지로 이동)
  const handleEditPost = (post) => {
    // TODO: 수정 페이지 구현 필요
    alert('수정 기능은 추후 구현 예정입니다.');
  };

  // 3. 페이지네이션 로직
  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentPosts = posts.slice(indexOfFirstItem, indexOfLastItem);
  const totalPages = Math.ceil(posts.length / itemsPerPage);

  // 검색 시 페이지 초기화
  const handleSearch = (query) => {
    setSearchQuery(query);
    setCurrentPage(1);
  };

  // 페이지 변경 핸들러
  const handlePageChange = (pageNumber) => {
    setCurrentPage(pageNumber);
  };

  // 상세페이지로 이동 (상세 API 호출하여 댓글 포함 데이터 가져오기)
  const handlePostClick = async (post) => {
    try {
      const response = await fetch(`${API_BASE}/posts/${post.id}/`, {
        credentials: 'include',
      });
      const data = await response.json();

      if (data.access_denied) {
        alert(data.message || '이 게시글에 접근할 권한이 없습니다.');
        return;
      }

      setSelectedPost({
        ...data,
        date: formatDate(data.created_at),
      });
      window.scrollTo(0, 0);
    } catch (error) {
      console.error('Failed to fetch post detail:', error);
      alert('게시글을 불러오는데 실패했습니다.');
    }
  };

  // 작성 페이지 렌더링
  if (isCreating) {
    return <PostCreate onBack={() => setIsCreating(false)} onSubmit={handleCreatePost} currentUser={currentUser} />;
  }

  // 상세페이지가 선택되면 PostDetail 렌더링
  if (selectedPost) {
    return (
      <PostDetail
        post={selectedPost}
        onBack={() => setSelectedPost(null)}
        onCommentSubmit={handleCommentSubmit}
        onCommentUpdate={handleCommentUpdate}
        onCommentDelete={handleCommentDelete}
        onEdit={handleEditPost}
        onDelete={handleDeletePost}
        currentUser={currentUser}
      />
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 p-8 flex flex-col font-sans">

      <div className="max-w-7xl mx-auto w-full">
        {/* Header Section */}
        <h1 className="text-2xl font-bold mb-6 text-gray-900">문의하기</h1>

        {/* Search Bar */}
        <div className="flex items-center gap-3 mb-6">
          {/* Filter Dropdown */}
          <div className="relative">
            <button
              onClick={() => setShowFilterDropdown(!showFilterDropdown)}
              className="flex items-center gap-2 px-4 py-2.5 bg-white border border-gray-200 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
            >
              <Filter size={16} />
              {filterOptions.find(opt => opt.value === filterType)?.label}
              <ChevronDown size={16} />
            </button>
            {showFilterDropdown && (
              <div className="absolute top-full left-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-10 min-w-[120px]">
                {filterOptions.map(option => (
                  <button
                    key={option.value}
                    onClick={() => {
                      setFilterType(option.value);
                      setShowFilterDropdown(false);
                      setCurrentPage(1);
                    }}
                    className={`w-full text-left px-4 py-2 text-sm hover:bg-gray-50 first:rounded-t-lg last:rounded-b-lg ${
                      filterType === option.value ? 'bg-emerald-50 text-emerald-600' : 'text-gray-700'
                    }`}
                  >
                    {option.label}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Search Input */}
          <div className="relative flex-1 max-w-md">
            <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              placeholder="검색어를 입력하세요..."
              className="w-full pl-10 pr-4 py-2.5 bg-white border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
            />
            {searchQuery && (
              <button
                onClick={() => handleSearch('')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                <X size={16} />
              </button>
            )}
          </div>

          {/* Results Count */}
          {searchQuery && (
            <span className="text-sm text-gray-500">
              {posts.length}개 결과
            </span>
          )}
        </div>

        <div className="flex justify-end items-center mb-8">
          <button
            onClick={() => setIsCreating(true)}
            className="flex items-center gap-2 bg-emerald-500 hover:bg-emerald-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            <Plus size={18} />
            글쓰기
          </button>
        </div>

        {/* Grid Container */}
        {loading ? (
          <div className="flex flex-col items-center justify-center py-20 text-gray-500">
            <div className="w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin mb-4"></div>
            <p className="text-sm">로딩 중...</p>
          </div>
        ) : posts.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-gray-500">
            <Search size={48} className="mb-4 text-gray-300" />
            <p className="text-lg font-medium">{searchQuery ? '검색 결과가 없습니다' : '게시글이 없습니다'}</p>
            <p className="text-sm mt-1">{searchQuery ? '다른 검색어를 입력해보세요' : '첫 게시글을 작성해보세요!'}</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-10">
            {currentPosts.map((post) => (
              <div
                key={post.id}
                onClick={() => handlePostClick(post)}
                className="bg-white rounded-xl p-6 border border-gray-100 hover:border-gray-300 transition-all flex flex-col h-[320px] shadow-md shadow-gray-200 hover:shadow-lg hover:shadow-gray-300 cursor-pointer"
              >
                {/* Author Info */}
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 bg-gray-300 rounded-full flex items-center justify-center flex-shrink-0">
                    <span className="text-gray-600 font-medium text-sm">
                      {post.user_name?.charAt(0)?.toUpperCase() || '?'}
                    </span>
                  </div>
                  <div className="flex flex-col">
                    <span className="text-sm font-semibold text-gray-900">{post.user_name || 'Anonymous'}</span>
                    <span className="text-xs text-gray-500 font-normal">{post.user_deptname || ''}</span>
                  </div>
                </div>

                {/* Tags */}
                {post.tags && post.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1 mb-3">
                    {post.tags.slice(0, 3).map((tag, idx) => (
                      <span
                        key={idx}
                        className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded-full"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                )}

                {/* Content */}
                <h3 className="text-lg font-bold text-gray-900 mb-3 leading-snug truncate flex items-center gap-2">
                  {post.is_private && <Lock size={16} className="text-gray-400 flex-shrink-0" />}
                  {post.title}
                </h3>
                <p className="text-gray-600 text-sm leading-relaxed mb-6 line-clamp-3 flex-grow">
                  {post.content}
                </p>

                {/* Footer */}
                <div className="mt-auto flex items-center justify-between pt-4 border-t border-gray-100">
                  <span className="text-xs text-gray-500 font-medium">Read update</span>

                  <div className="flex items-center gap-2 text-gray-500 hover:text-gray-900 transition-colors cursor-pointer">
                    <MessageSquare size={16} />
                    <span className="text-xs font-medium">{post.comments}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Pagination Controls */}
        {totalPages > 1 && (
          <div className="flex justify-center items-center gap-2 mt-auto">
            <button
              onClick={() => handlePageChange(currentPage - 1)}
              disabled={currentPage === 1}
              className={`p-2 rounded-lg ${currentPage === 1 ? 'text-gray-300 cursor-not-allowed' : 'text-gray-600 hover:bg-gray-200'}`}
            >
              <ChevronLeft size={20} />
            </button>

            {Array.from({ length: totalPages }, (_, i) => i + 1).map((number) => (
              <button
                key={number}
                onClick={() => handlePageChange(number)}
                className={`w-8 h-8 rounded-lg text-sm font-medium transition-all ${
                  currentPage === number
                    ? 'bg-gray-900 text-white'
                    : 'text-gray-600 hover:bg-gray-200 hover:text-gray-900'
                }`}
              >
                {number}
              </button>
            ))}

            <button
              onClick={() => handlePageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
              className={`p-2 rounded-lg ${currentPage === totalPages ? 'text-gray-300 cursor-not-allowed' : 'text-gray-600 hover:bg-gray-200'}`}
            >
              <ChevronRight size={20} />
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default BoardList;
export { PostCreate, PostDetail };

// 독립 SPA 렌더링 (일반적인 React 앱처럼 동작)
if (typeof document !== 'undefined') {
  const rootElement = document.getElementById('root');
  if (rootElement) {
    ReactDOM.createRoot(rootElement).render(
      <React.StrictMode>
        <BoardList />
      </React.StrictMode>
    );
  }
}
