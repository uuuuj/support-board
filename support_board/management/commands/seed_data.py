import random
from django.core.management.base import BaseCommand
from support_board.models import Post, Comment, Tag


class Command(BaseCommand):
    help = '더미 데이터를 생성합니다'

    def add_arguments(self, parser):
        parser.add_argument(
            '--posts',
            type=int,
            default=30,
            help='생성할 게시글 수 (기본값: 30)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='기존 데이터 삭제 후 생성'
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('기존 데이터 삭제 중...')
            Comment.objects.all().delete()
            Post.objects.all().delete()
            Tag.objects.all().delete()

        # 태그 생성
        tag_names = [
            'feature', 'bug', 'enhancement', 'question', 'discussion',
            'announcement', 'update', 'help', 'documentation', 'feedback'
        ]
        tags = []
        for name in tag_names:
            tag, _ = Tag.objects.get_or_create(name=name)
            tags.append(tag)
        self.stdout.write(f'태그 {len(tags)}개 생성/확인 완료')

        # 작성자 목록
        authors = [
            'Ami Asadi', 'Mo Mayeri', 'Jacob Kim', 'Sarah Chen',
            'David Park', 'Emily Lee', 'Michael Jung', 'Lisa Wang',
            'James Choi', 'Anna Yoon'
        ]

        # 게시글 제목 템플릿
        title_templates = [
            'Update Log #{}: Enhanced Features',
            'Bug Fix #{}: Performance Improvements',
            'New Feature #{}: User Experience Update',
            'Announcement #{}: Platform Changes',
            'Discussion #{}: Community Feedback',
            'Question #{}: How to use the new feature?',
            'Enhancement #{}: UI/UX Improvements',
            'Documentation #{}: API Reference Update',
            'Feedback #{}: Your thoughts needed',
            'Help #{}: Need assistance with setup',
        ]

        # 게시글 내용 템플릿
        content_templates = [
            "We've tightened the experience across the board: clearer language, dependable emails, smarter moderation, and worked on performance. Native Events is about to land with end-to-end creation tools.",
            "This update includes several bug fixes and performance improvements. We've addressed the issues reported by our community and made the platform more stable.",
            "Introducing a new feature that allows you to customize your dashboard. You can now drag and drop widgets, change themes, and personalize your workspace.",
            "We're excited to announce major platform changes coming next month. This includes a redesigned navigation, improved search functionality, and faster loading times.",
            "We'd love to hear your thoughts on the recent changes. Please share your feedback in the comments below. Your input helps us improve the platform.",
            "I'm having trouble understanding how to use the new feature. Can someone explain the steps or point me to the documentation?",
            "Based on user feedback, we've made several UI/UX improvements. The interface is now more intuitive and easier to navigate.",
            "We've updated the API documentation with new endpoints and examples. Check out the updated reference guide for more details.",
            "We're collecting feedback on the proposed changes. Please let us know what you think about the new direction we're taking.",
            "I need help setting up the integration. Has anyone successfully configured this? Any tips would be appreciated.",
        ]

        # 댓글 내용 템플릿
        comment_templates = [
            "Thanks for the update! This is exactly what we needed.",
            "Great work! Looking forward to trying this out.",
            "I have a question about this. Can you elaborate on the implementation?",
            "This is fantastic! The team has done an amazing job.",
            "I noticed a small issue. Will report it in the bug tracker.",
            "Love the new changes! Keep up the great work.",
            "Could you provide more details on the timeline?",
            "This solved my problem. Thank you so much!",
            "Interesting approach. I'd suggest considering alternative solutions too.",
            "Well documented and easy to follow. Appreciate the effort!",
        ]

        # 게시글 생성
        posts_count = options['posts']
        self.stdout.write(f'게시글 {posts_count}개 생성 중...')

        for i in range(posts_count):
            title = random.choice(title_templates).format(i + 1)
            content = random.choice(content_templates)
            author = random.choice(authors)
            is_resolved = random.choice([True, False, False, False])  # 25% 확률로 resolved

            post = Post.objects.create(
                title=title,
                content=content,
                user_name=author,
                is_resolved=is_resolved,
            )

            # 랜덤하게 1~3개의 태그 추가
            post_tags = random.sample(tags, random.randint(1, 3))
            post.tags.set(post_tags)

            # 랜덤하게 0~5개의 댓글 추가
            num_comments = random.randint(0, 5)
            for _ in range(num_comments):
                Comment.objects.create(
                    post=post,
                    content=random.choice(comment_templates),
                    user_name=random.choice(authors),
                )

        self.stdout.write(self.style.SUCCESS(f'더미 데이터 생성 완료: 게시글 {posts_count}개'))
