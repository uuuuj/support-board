import React, { useState } from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
// 아이콘 라이브러리가 설치되어 있어야 합니다. (터미널에: npm install lucide-react)
import { MessageSquare, ChevronLeft, ChevronRight, ArrowLeft, MoreHorizontal, Plus, X } from 'lucide-react';

// 게시글 작성 컴포넌트
const PostCreate = ({ onBack, onSubmit }) => {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [resolved, setResolved] = useState(false);
  const [tags, setTags] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!title.trim() || !content.trim()) {
      alert('제목과 내용을 입력해주세요.');
      return;
    }
    onSubmit({ title, content, author: 'Anonymous' });
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

          {/* Resolved Toggle */}
          <div className="flex items-center justify-between py-2">
            <span className="text-sm font-semibold text-gray-900">Resolved</span>
            <button
              type="button"
              onClick={() => setResolved(!resolved)}
              className={`w-12 h-7 rounded-full transition-colors ${resolved ? 'bg-emerald-500' : 'bg-gray-200'}`}
            >
              <div className={`w-5 h-5 bg-white rounded-full shadow-sm transition-transform ${resolved ? 'translate-x-6' : 'translate-x-1'}`} />
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

          {/* SEO Options */}
          <div className="flex items-center justify-between py-3 border-t border-gray-100">
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold text-gray-900">SEO options</span>
              <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
              </svg>
            </div>
            <Plus size={18} className="text-gray-400" />
          </div>

          {/* Advanced Options */}
          <div className="flex items-center justify-between py-3 border-t border-gray-100">
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold text-gray-900">Advanced options</span>
              <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
              </svg>
            </div>
            <Plus size={18} className="text-gray-400" />
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

// 더미 댓글 데이터
const dummyComments = [
  {
    id: 1,
    author: "Mari Babikova",
    initials: "MB",
    bgColor: "bg-amber-200",
    textColor: "text-amber-700",
    date: "3 days ago",
    role: null,
    content: "Thanks Jacob! That would be great.",
    likes: 0,
  },
  {
    id: 2,
    author: "Sil",
    initials: "S",
    bgColor: "bg-purple-500",
    textColor: "text-white",
    date: "9 days ago",
    role: "Sr Program Manager, Community Experts at Adobe",
    content: `Love the "add to calendar" feature!\n\nQuestions:\n1- Will this be added to the main Event CMS type, or would we be able to add this feature to any CMS format?\n2- Will there be an option to add all events within a space to our calendars? aka sync all the invites, or just one by one?`,
    likes: 1,
  },
  {
    id: 3,
    author: "Ami Asadi",
    initials: "A",
    bgColor: "bg-gray-200",
    textColor: "text-gray-600",
    date: "8 days ago",
    role: null,
    content: `Glad you liked it, Sil! We'll be sharing more in the launch party as well, features like recurring events, event embedding and what's coming next.\n\n1. Easy Events is tied to the Event Space template to keep the experience smooth, simple, and intuitive. That said, events can still be embedded into any post, so you can surface them in any space as needed.\n\n2. While we do support recurring events in the Add to Calendar flow. At the moment, however, batch-adding or syncing all events in a space to a calendar isn't supported, so events need to be added one by one.\n\nLooking forward to sharing more soon!`,
    likes: 0,
  },
];

// 상세페이지 컴포넌트
const PostDetail = ({ post, onBack }) => {
  return (
    <div className="min-h-screen bg-white font-sans">
      {/* Header */}
      <div className="sticky top-0 bg-white border-b border-gray-100 px-6 py-4">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={onBack}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <ArrowLeft size={20} className="text-gray-600" />
            </button>
            <span className="font-semibold text-gray-900">Product Updates</span>
          </div>
          <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <MoreHorizontal size={20} className="text-gray-600" />
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-6 py-8">
        {/* Author Info */}
        <div className="flex items-center gap-3 mb-6">
          <div className="w-12 h-12 bg-gray-200 rounded-full flex items-center justify-center">
            <span className="text-gray-600 font-semibold text-lg">
              {post.author.charAt(0)}
            </span>
          </div>
          <div>
            <p className="font-semibold text-gray-900">{post.author}</p>
            <p className="text-sm text-gray-500">{post.date} · Posted in Product Updates</p>
          </div>
        </div>

        {/* Title */}
        <h1 className="text-2xl font-bold text-gray-900 mb-6">
          {post.title}
        </h1>

        {/* Body */}
        <div className="prose prose-gray max-w-none">
          <p className="text-gray-700 leading-relaxed mb-6">
            {post.content}
          </p>
          <p className="text-gray-700 leading-relaxed mb-6">
            And the big one: <strong>Native Events</strong> is about to land. End-to-end creation, view-vs-attendance insights, post embeds, hybrid (in-person & virtual) support, and recurring RSVPs.
          </p>
        </div>

        {/* Comments Section */}
        <div className="mt-10 pb-24">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-gray-900">Comments</h2>
            <span className="text-sm text-gray-500">Sort by newest first</span>
          </div>

          <div className="space-y-6">
            {dummyComments.map((comment) => (
              <div key={comment.id} className="flex gap-3">
                {/* Avatar */}
                <div className={`w-10 h-10 ${comment.bgColor} rounded-full flex items-center justify-center flex-shrink-0`}>
                  <span className={`${comment.textColor} font-semibold text-sm`}>
                    {comment.initials}
                  </span>
                </div>

                {/* Comment Content */}
                <div className="flex-1">
                  <div className="flex items-start justify-between">
                    <div>
                      <span className="font-semibold text-gray-900">{comment.author}</span>
                      <p className="text-sm text-gray-500">
                        {comment.date}
                        {comment.role && ` · ${comment.role}`}
                      </p>
                    </div>
                    <button className="p-1 hover:bg-gray-100 rounded transition-colors">
                      <MoreHorizontal size={16} className="text-gray-400" />
                    </button>
                  </div>

                  <div className="mt-3 text-gray-700 whitespace-pre-line leading-relaxed">
                    {comment.content}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Comment Input */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 px-6 py-4">
        <div className="max-w-4xl mx-auto flex items-center gap-3">
          <div className="w-10 h-10 bg-emerald-500 rounded-full flex items-center justify-center">
            <span className="text-white font-semibold">G</span>
          </div>
          <input
            type="text"
            placeholder="What are your thoughts?"
            className="flex-1 bg-gray-100 rounded-full px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
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
  const itemsPerPage = 9;

  // 2. 더미 데이터 생성 (페이지네이션 테스트를 위해 24개 생성)
  const [posts, setPosts] = useState(Array.from({ length: 24 }, (_, i) => ({
    id: i + 1,
    author: i % 2 === 0 ? "Ami Asadi" : "Mo Mayeri",
    date: `${i + 1} days ago`,
    title: `Update Log #${i + 1}: Enhanced Features`,
    content: "We've tightened the experience across the board: clearer language, dependable emails, smarter moderation, and worked on performance. Native Events is about to land with end-to-end creation tools.",
    comments: Math.floor(Math.random() * 20),
  })));

  // 새 게시글 작성 핸들러
  const handleCreatePost = (newPost) => {
    const post = {
      id: posts.length + 1,
      ...newPost,
      date: 'Just now',
      comments: 0,
    };
    setPosts([post, ...posts]);
    setIsCreating(false);
  };

  // 3. 페이지네이션 로직
  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentPosts = posts.slice(indexOfFirstItem, indexOfLastItem);
  const totalPages = Math.ceil(posts.length / itemsPerPage);

  // 페이지 변경 핸들러
  const handlePageChange = (pageNumber) => {
    setCurrentPage(pageNumber);
  };

  // 상세페이지로 이동
  const handlePostClick = (post) => {
    setSelectedPost(post);
    window.scrollTo(0, 0);
  };

  // 작성 페이지 렌더링
  if (isCreating) {
    return <PostCreate onBack={() => setIsCreating(false)} onSubmit={handleCreatePost} />;
  }

  // 상세페이지가 선택되면 PostDetail 렌더링
  if (selectedPost) {
    return <PostDetail post={selectedPost} onBack={() => setSelectedPost(null)} />;
  }

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 p-8 flex flex-col font-sans">
      
      <div className="max-w-7xl mx-auto w-full">
        {/* Header Section */}
        <h1 className="text-2xl font-bold mb-6 text-gray-900">What's new</h1>
        
        <div className="flex justify-between items-center mb-8">
          <div className="flex gap-4 items-center">
            <button className="bg-gray-900 hover:bg-gray-800 text-white px-5 py-2 rounded-full text-sm font-medium transition-colors">
              Product
            </button>
            <button className="text-gray-500 hover:text-gray-900 px-2 text-sm font-medium transition-colors">
              Events
            </button>
          </div>

          <button
            onClick={() => setIsCreating(true)}
            className="flex items-center gap-2 bg-emerald-500 hover:bg-emerald-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            <Plus size={18} />
            글쓰기
          </button>
        </div>

        {/* Grid Container */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-10">
          {currentPosts.map((post) => (
            <div
              key={post.id}
              onClick={() => handlePostClick(post)}
              className="bg-white rounded-xl p-6 border border-gray-100 hover:border-gray-300 transition-all flex flex-col h-[320px] shadow-md shadow-gray-200 hover:shadow-lg hover:shadow-gray-300 cursor-pointer"
            >
              {/* Author Info */}
              <div className="flex items-center gap-3 mb-4">
                <div className="flex flex-col">
                  <span className="text-sm font-semibold text-gray-900">{post.author}</span>
                  <span className="text-xs text-gray-500">{post.date}</span>
                </div>
              </div>

              {/* Content */}
              <h3 className="text-lg font-bold text-gray-900 mb-3 leading-snug truncate">
                {post.title}
              </h3>
              <p className="text-gray-600 text-sm leading-relaxed mb-6 line-clamp-4 flex-grow">
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

// 화면에 렌더링
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BoardList />
  </React.StrictMode>
);