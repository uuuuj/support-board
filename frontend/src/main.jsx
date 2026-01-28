import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import { MessageSquare, ChevronLeft, ChevronRight, ArrowLeft, MoreHorizontal, Plus, X, Search, Filter, ChevronDown, Lock } from 'lucide-react';

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
    <div className="sb-min-h-screen sb-bg-gray-100 sb-font-sans sb-flex sb-items-center sb-justify-center sb-p-4">
      <div className="sb-bg-white sb-rounded-2xl sb-shadow-sm sb-max-w-2xl sb-w-full sb-p-8">
        {/* Header */}
        <div className="sb-flex sb-items-center sb-gap-3 sb-mb-8">
          <button
            onClick={onBack}
            className="sb-p-1 hover:sb-bg-gray-100 sb-rounded-lg sb-transition-colors"
          >
            <ArrowLeft size={20} className="sb-text-gray-600" />
          </button>
          <h1 className="sb-text-lg sb-font-semibold sb-text-gray-900">Create a new question</h1>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="sb-space-y-6">
          {/* Title */}
          <div>
            <label className="sb-block sb-text-sm sb-font-semibold sb-text-gray-900 sb-mb-2">
              Title
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="제목을 입력하세요"
              className="sb-w-full sb-px-4 sb-py-3 sb-border sb-border-gray-200 sb-rounded-lg focus:sb-outline-none focus:sb-ring-2 focus:sb-ring-emerald-500 focus:sb-border-transparent"
            />
          </div>

          {/* Content */}
          <div>
            <label className="sb-block sb-text-sm sb-font-semibold sb-text-gray-900 sb-mb-2">
              Content
            </label>
            <div className="sb-border sb-border-gray-200 sb-rounded-lg sb-overflow-hidden">
              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="What are your thoughts?"
                rows={8}
                className="sb-w-full sb-px-4 sb-py-3 focus:sb-outline-none sb-resize-none"
              />
              {/* Toolbar */}
              <div className="sb-flex sb-items-center sb-gap-1 sb-px-3 sb-py-2 sb-border-t sb-border-gray-100">
                <button type="button" className="sb-p-2 hover:sb-bg-gray-100 sb-rounded-lg sb-transition-colors">
                  <svg className="sb-w-5 sb-h-5 sb-text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </button>
                <button type="button" className="sb-p-2 hover:sb-bg-gray-100 sb-rounded-lg sb-transition-colors sb-text-gray-500 sb-font-semibold sb-text-sm">
                  Aa
                </button>
                <button type="button" className="sb-p-2 hover:sb-bg-gray-100 sb-rounded-lg sb-transition-colors">
                  <svg className="sb-w-5 sb-h-5 sb-text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <circle cx="12" cy="12" r="10" strokeWidth={2} />
                    <path strokeLinecap="round" strokeWidth={2} d="M8 14s1.5 2 4 2 4-2 4-2" />
                    <circle cx="9" cy="9" r="1" fill="currentColor" />
                    <circle cx="15" cy="9" r="1" fill="currentColor" />
                  </svg>
                </button>
                <button type="button" className="sb-p-2 hover:sb-bg-gray-100 sb-rounded-lg sb-transition-colors">
                  <svg className="sb-w-5 sb-h-5 sb-text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <rect x="3" y="3" width="18" height="18" rx="2" strokeWidth={2} />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 15l5-5 4 4 5-5 4 4" />
                  </svg>
                </button>
                <button type="button" className="sb-p-2 hover:sb-bg-gray-100 sb-rounded-lg sb-transition-colors">
                  <svg className="sb-w-5 sb-h-5 sb-text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                  </svg>
                </button>
              </div>
            </div>
          </div>

          {/* Private Toggle */}
          <div className="sb-flex sb-items-center sb-justify-between sb-py-2">
            <div className="sb-flex sb-items-center sb-gap-2">
              <Lock size={16} className="sb-text-gray-500" />
              <span className="sb-text-sm sb-font-semibold sb-text-gray-900">비밀글</span>
              {!currentUser && (
                <span className="sb-text-xs sb-text-gray-400">(로그인 필요)</span>
              )}
            </div>
            <button
              type="button"
              onClick={() => currentUser && setIsPrivate(!isPrivate)}
              disabled={!currentUser}
              className={`sb-w-12 sb-h-7 sb-rounded-full sb-transition-colors ${isPrivate ? 'sb-bg-emerald-500' : 'sb-bg-gray-200'} ${!currentUser ? 'sb-opacity-50 sb-cursor-not-allowed' : ''}`}
            >
              <div className={`sb-w-5 sb-h-5 sb-bg-white sb-rounded-full sb-shadow-sm sb-transition-transform ${isPrivate ? 'sb-translate-x-6' : 'sb-translate-x-1'}`} />
            </button>
          </div>

          {/* Tags */}
          <div>
            <label className="sb-block sb-text-sm sb-font-semibold sb-text-gray-900 sb-mb-2">
              Tags
            </label>
            <div className="sb-relative">
              <input
                type="text"
                value={tags}
                onChange={(e) => setTags(e.target.value)}
                placeholder="Add tags..."
                className="sb-w-full sb-px-4 sb-py-3 sb-border sb-border-gray-200 sb-rounded-lg focus:sb-outline-none focus:sb-ring-2 focus:sb-ring-emerald-500 focus:sb-border-transparent sb-pr-10"
              />
              <ChevronRight size={18} className="sb-absolute sb-right-3 sb-top-1/2 -sb-translate-y-1/2 sb-text-gray-400 sb-rotate-90" />
            </div>
          </div>

          {/* Buttons */}
          <div className="sb-flex sb-items-center sb-justify-end sb-gap-3 sb-pt-4">
            <button
              type="button"
              onClick={onBack}
              className="sb-px-6 sb-py-2.5 sb-border sb-border-gray-200 sb-rounded-full sb-text-sm sb-font-medium sb-text-gray-700 hover:sb-bg-gray-50 sb-transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="sb-px-6 sb-py-2.5 sb-bg-emerald-500 hover:sb-bg-emerald-600 sb-text-white sb-rounded-full sb-text-sm sb-font-medium sb-transition-colors"
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
const PostDetail = ({ post, onBack }) => {
  return (
    <div className="sb-min-h-screen sb-bg-white sb-font-sans">
      {/* Header */}
      <div className="sb-sticky sb-top-0 sb-bg-white sb-border-b sb-border-gray-100 sb-px-6 sb-py-4">
        <div className="sb-max-w-4xl sb-mx-auto sb-flex sb-items-center sb-justify-between">
          <div className="sb-flex sb-items-center sb-gap-3">
            <button
              onClick={onBack}
              className="sb-p-2 hover:sb-bg-gray-100 sb-rounded-lg sb-transition-colors"
            >
              <ArrowLeft size={20} className="sb-text-gray-600" />
            </button>
            <span className="sb-font-semibold sb-text-gray-900">게시글</span>
          </div>
          <button className="sb-p-2 hover:sb-bg-gray-100 sb-rounded-lg sb-transition-colors">
            <MoreHorizontal size={20} className="sb-text-gray-600" />
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="sb-max-w-4xl sb-mx-auto sb-px-6 sb-py-8">
        {/* Author Info */}
        <div className="sb-flex sb-items-center sb-gap-3 sb-mb-6">
          <div className="sb-w-12 sb-h-12 sb-bg-gray-300 sb-rounded-full sb-flex sb-items-center sb-justify-center sb-flex-shrink-0">
            <span className="sb-text-gray-600 sb-font-medium sb-text-lg">
              {post.user_name?.charAt(0)?.toUpperCase() || '?'}
            </span>
          </div>
          <div className="sb-flex sb-flex-col">
            <div className="sb-flex sb-items-center sb-gap-2">
              <span className="sb-font-semibold sb-text-gray-900">{post.user_name || 'Anonymous'}</span>
              <span className="sb-text-sm sb-text-gray-400">·</span>
              <span className="sb-text-sm sb-text-gray-500">{post.date}</span>
            </div>
            <p className="sb-text-sm sb-text-gray-500 sb-font-normal">{post.user_deptname || ''}</p>
          </div>
        </div>

        {/* Title */}
        <h1 className="sb-text-2xl sb-font-bold sb-text-gray-900 sb-mb-6">
          {post.title}
        </h1>

        {/* Body */}
        <div className="sb-prose sb-prose-gray sb-max-w-none">
          <p className="sb-text-gray-700 sb-leading-relaxed sb-mb-6 sb-whitespace-pre-line">
            {post.content}
          </p>
        </div>

        {/* Comments Section */}
        <div className="sb-mt-10 sb-pb-24">
          <div className="sb-flex sb-items-center sb-justify-between sb-mb-6">
            <h2 className="sb-text-lg sb-font-semibold sb-text-gray-900">Comments ({post.comments?.length || 0})</h2>
            <span className="sb-text-sm sb-text-gray-500">Sort by newest first</span>
          </div>

          <div className="sb-space-y-6">
            {post.comments && post.comments.length > 0 ? (
              post.comments.map((comment) => (
                <div key={comment.id} className="sb-flex sb-gap-3">
                  {/* Avatar */}
                  <div className="sb-w-10 sb-h-10 sb-bg-gray-300 sb-rounded-full sb-flex sb-items-center sb-justify-center sb-flex-shrink-0">
                    <span className="sb-text-gray-600 sb-font-medium sb-text-sm">
                      {comment.user_name?.charAt(0)?.toUpperCase() || '?'}
                    </span>
                  </div>

                  {/* Comment Content */}
                  <div className="sb-flex-1">
                    <div className="sb-flex sb-items-start sb-justify-between">
                      <div className="sb-flex sb-flex-col">
                        <div className="sb-flex sb-items-center sb-gap-2">
                          <span className="sb-font-semibold sb-text-gray-900">{comment.user_name || 'Anonymous'}</span>
                          <span className="sb-text-sm sb-text-gray-400">·</span>
                          <span className="sb-text-sm sb-text-gray-500">{formatDate(comment.created_at)}</span>
                        </div>
                        <p className="sb-text-xs sb-text-gray-500 sb-font-normal">{comment.user_deptname || ''}</p>
                      </div>
                      <button className="sb-p-1 hover:sb-bg-gray-100 sb-rounded sb-transition-colors">
                        <MoreHorizontal size={16} className="sb-text-gray-400" />
                      </button>
                    </div>

                    <div className="sb-mt-2 sb-text-gray-700 sb-whitespace-pre-line sb-leading-relaxed">
                      {comment.content}
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <p className="sb-text-gray-500 sb-text-center sb-py-8">아직 댓글이 없습니다.</p>
            )}
          </div>
        </div>
      </div>

      {/* Comment Input */}
      <div className="sb-fixed sb-bottom-0 sb-left-0 sb-right-0 sb-bg-white sb-border-t sb-border-gray-200 sb-px-6 sb-py-4">
        <div className="sb-max-w-4xl sb-mx-auto sb-flex sb-items-center sb-gap-3">
          <div className="sb-w-10 sb-h-10 sb-bg-emerald-500 sb-rounded-full sb-flex sb-items-center sb-justify-center">
            <span className="sb-text-white sb-font-semibold">G</span>
          </div>
          <input
            type="text"
            placeholder="What are your thoughts?"
            className="sb-flex-1 sb-bg-gray-100 sb-rounded-full sb-px-4 sb-py-3 sb-text-sm focus:sb-outline-none focus:sb-ring-2 focus:sb-ring-emerald-500"
          />
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
    return <PostDetail post={selectedPost} onBack={() => setSelectedPost(null)} />;
  }

  return (
    <div className="sb-min-h-screen sb-bg-gray-50 sb-text-gray-900 sb-p-8 sb-flex sb-flex-col sb-font-sans">

      <div className="sb-max-w-7xl sb-mx-auto sb-w-full">
        {/* Header Section */}
        <h1 className="sb-text-2xl sb-font-bold sb-mb-6 sb-text-gray-900">문의하기</h1>

        {/* Search Bar */}
        <div className="sb-flex sb-items-center sb-gap-3 sb-mb-6">
          {/* Filter Dropdown */}
          <div className="sb-relative">
            <button
              onClick={() => setShowFilterDropdown(!showFilterDropdown)}
              className="sb-flex sb-items-center sb-gap-2 sb-px-4 sb-py-2.5 sb-bg-white sb-border sb-border-gray-200 sb-rounded-lg sb-text-sm sb-font-medium sb-text-gray-700 hover:sb-bg-gray-50 sb-transition-colors"
            >
              <Filter size={16} />
              {filterOptions.find(opt => opt.value === filterType)?.label}
              <ChevronDown size={16} />
            </button>
            {showFilterDropdown && (
              <div className="sb-absolute sb-top-full sb-left-0 sb-mt-1 sb-bg-white sb-border sb-border-gray-200 sb-rounded-lg sb-shadow-lg sb-z-10 sb-min-w-[120px]">
                {filterOptions.map(option => (
                  <button
                    key={option.value}
                    onClick={() => {
                      setFilterType(option.value);
                      setShowFilterDropdown(false);
                      setCurrentPage(1);
                    }}
                    className={`sb-w-full sb-text-left sb-px-4 sb-py-2 sb-text-sm hover:sb-bg-gray-50 first:sb-rounded-t-lg last:sb-rounded-b-lg ${
                      filterType === option.value ? 'sb-bg-emerald-50 sb-text-emerald-600' : 'sb-text-gray-700'
                    }`}
                  >
                    {option.label}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Search Input */}
          <div className="sb-relative sb-flex-1 sb-max-w-md">
            <Search size={18} className="sb-absolute sb-left-3 sb-top-1/2 -sb-translate-y-1/2 sb-text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              placeholder="검색어를 입력하세요..."
              className="sb-w-full sb-pl-10 sb-pr-4 sb-py-2.5 sb-bg-white sb-border sb-border-gray-200 sb-rounded-lg sb-text-sm focus:sb-outline-none focus:sb-ring-2 focus:sb-ring-emerald-500 focus:sb-border-transparent"
            />
            {searchQuery && (
              <button
                onClick={() => handleSearch('')}
                className="sb-absolute sb-right-3 sb-top-1/2 -sb-translate-y-1/2 sb-text-gray-400 hover:sb-text-gray-600"
              >
                <X size={16} />
              </button>
            )}
          </div>

          {/* Results Count */}
          {searchQuery && (
            <span className="sb-text-sm sb-text-gray-500">
              {posts.length}개 결과
            </span>
          )}
        </div>

        <div className="sb-flex sb-justify-end sb-items-center sb-mb-8">
          <button
            onClick={() => setIsCreating(true)}
            className="sb-flex sb-items-center sb-gap-2 sb-bg-emerald-500 hover:sb-bg-emerald-600 sb-text-white sb-px-4 sb-py-2 sb-rounded-lg sb-text-sm sb-font-medium sb-transition-colors"
          >
            <Plus size={18} />
            글쓰기
          </button>
        </div>

        {/* Grid Container */}
        {loading ? (
          <div className="sb-flex sb-flex-col sb-items-center sb-justify-center sb-py-20 sb-text-gray-500">
            <div className="sb-w-8 sb-h-8 sb-border-4 sb-border-emerald-500 sb-border-t-transparent sb-rounded-full sb-animate-spin sb-mb-4"></div>
            <p className="sb-text-sm">로딩 중...</p>
          </div>
        ) : posts.length === 0 ? (
          <div className="sb-flex sb-flex-col sb-items-center sb-justify-center sb-py-20 sb-text-gray-500">
            <Search size={48} className="sb-mb-4 sb-text-gray-300" />
            <p className="sb-text-lg sb-font-medium">{searchQuery ? '검색 결과가 없습니다' : '게시글이 없습니다'}</p>
            <p className="sb-text-sm sb-mt-1">{searchQuery ? '다른 검색어를 입력해보세요' : '첫 게시글을 작성해보세요!'}</p>
          </div>
        ) : (
          <div className="sb-grid sb-grid-cols-1 md:sb-grid-cols-2 lg:sb-grid-cols-3 sb-gap-6 sb-mb-10">
            {currentPosts.map((post) => (
              <div
                key={post.id}
                onClick={() => handlePostClick(post)}
                className="sb-bg-white sb-rounded-xl sb-p-6 sb-border sb-border-gray-100 hover:sb-border-gray-300 sb-transition-all sb-flex sb-flex-col sb-h-[320px] sb-shadow-md sb-shadow-gray-200 hover:sb-shadow-lg hover:sb-shadow-gray-300 sb-cursor-pointer"
              >
                {/* Author Info */}
                <div className="sb-flex sb-items-center sb-gap-3 sb-mb-4">
                  <div className="sb-w-10 sb-h-10 sb-bg-gray-300 sb-rounded-full sb-flex sb-items-center sb-justify-center sb-flex-shrink-0">
                    <span className="sb-text-gray-600 sb-font-medium sb-text-sm">
                      {post.user_name?.charAt(0)?.toUpperCase() || '?'}
                    </span>
                  </div>
                  <div className="sb-flex sb-flex-col">
                    <span className="sb-text-sm sb-font-semibold sb-text-gray-900">{post.user_name || 'Anonymous'}</span>
                    <span className="sb-text-xs sb-text-gray-500 sb-font-normal">{post.user_deptname || ''}</span>
                  </div>
                </div>

                {/* Tags */}
                {post.tags && post.tags.length > 0 && (
                  <div className="sb-flex sb-flex-wrap sb-gap-1 sb-mb-3">
                    {post.tags.slice(0, 3).map((tag, idx) => (
                      <span
                        key={idx}
                        className="sb-px-2 sb-py-0.5 sb-bg-gray-100 sb-text-gray-600 sb-text-xs sb-rounded-full"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                )}

                {/* Content */}
                <h3 className="sb-text-lg sb-font-bold sb-text-gray-900 sb-mb-3 sb-leading-snug sb-truncate sb-flex sb-items-center sb-gap-2">
                  {post.is_private && <Lock size={16} className="sb-text-gray-400 sb-flex-shrink-0" />}
                  {post.title}
                </h3>
                <p className="sb-text-gray-600 sb-text-sm sb-leading-relaxed sb-mb-6 sb-line-clamp-3 sb-flex-grow">
                  {post.content}
                </p>

                {/* Footer */}
                <div className="sb-mt-auto sb-flex sb-items-center sb-justify-between sb-pt-4 sb-border-t sb-border-gray-100">
                  <span className="sb-text-xs sb-text-gray-500 sb-font-medium">Read update</span>

                  <div className="sb-flex sb-items-center sb-gap-2 sb-text-gray-500 hover:sb-text-gray-900 sb-transition-colors sb-cursor-pointer">
                    <MessageSquare size={16} />
                    <span className="sb-text-xs sb-font-medium">{post.comments}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Pagination Controls */}
        {totalPages > 1 && (
          <div className="sb-flex sb-justify-center sb-items-center sb-gap-2 sb-mt-auto">
            <button
              onClick={() => handlePageChange(currentPage - 1)}
              disabled={currentPage === 1}
              className={`sb-p-2 sb-rounded-lg ${currentPage === 1 ? 'sb-text-gray-300 sb-cursor-not-allowed' : 'sb-text-gray-600 hover:sb-bg-gray-200'}`}
            >
              <ChevronLeft size={20} />
            </button>

            {Array.from({ length: totalPages }, (_, i) => i + 1).map((number) => (
              <button
                key={number}
                onClick={() => handlePageChange(number)}
                className={`sb-w-8 sb-h-8 sb-rounded-lg sb-text-sm sb-font-medium sb-transition-all ${
                  currentPage === number
                    ? 'sb-bg-gray-900 sb-text-white'
                    : 'sb-text-gray-600 hover:sb-bg-gray-200 hover:sb-text-gray-900'
                }`}
              >
                {number}
              </button>
            ))}

            <button
              onClick={() => handlePageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
              className={`sb-p-2 sb-rounded-lg ${currentPage === totalPages ? 'sb-text-gray-300 sb-cursor-not-allowed' : 'sb-text-gray-600 hover:sb-bg-gray-200'}`}
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
