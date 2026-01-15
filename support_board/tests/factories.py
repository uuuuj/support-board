"""Factory Boy를 사용한 테스트 데이터 팩토리.

테스트에 필요한 모델 인스턴스를 생성하는 팩토리 클래스들입니다.
"""

import factory
from factory.django import DjangoModelFactory

from support_board.models import Post, Comment, Tag


# TODO: User 모델이 다른 프로젝트에 있으므로 User factory는 해당 프로젝트에서 정의
# class UserFactory(DjangoModelFactory):
#     """User 테스트 데이터 팩토리."""
#
#     class Meta:
#         model = User  # 다른 프로젝트의 User 모델
#
#     user_id = factory.Sequence(lambda n: f'user-{n:03d}')
#     username = factory.Faker('user_name')
#     is_admin = False


class TagFactory(DjangoModelFactory):
    """Tag 테스트 데이터 팩토리.

    Example:
        >>> tag = TagFactory()
        >>> tag = TagFactory(name='Django')
    """

    class Meta:
        model = Tag
        django_get_or_create = ('name',)

    name = factory.Sequence(lambda n: f'Tag{n}')


class PostFactory(DjangoModelFactory):
    """Post 테스트 데이터 팩토리.

    Example:
        >>> post = PostFactory()
        >>> post = PostFactory(title='커스텀 제목', is_private=True)
        >>> post = PostFactory.create_batch(5)  # 5개 생성
    """

    class Meta:
        model = Post

    title = factory.Sequence(lambda n: f'테스트 게시글 {n}')
    content = factory.Faker('paragraph', locale='ko_KR')
    user_name = factory.Faker('name', locale='ko_KR')
    user_id = factory.Sequence(lambda n: f'user-{n:03d}')
    user_compname = factory.Faker('company', locale='ko_KR')
    user_deptname = factory.LazyFunction(lambda: '개발팀')
    is_resolved = False
    is_private = False

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        """태그 추가.

        Example:
            >>> post = PostFactory(tags=['Django', 'Python'])
            >>> post = PostFactory(tags=[tag1, tag2])  # 기존 Tag 인스턴스
        """
        if not create:
            return

        if extracted:
            for tag in extracted:
                if isinstance(tag, str):
                    tag_obj, _ = Tag.objects.get_or_create(name=tag)
                    self.tags.add(tag_obj)
                else:
                    self.tags.add(tag)


class CommentFactory(DjangoModelFactory):
    """Comment 테스트 데이터 팩토리.

    Example:
        >>> comment = CommentFactory()
        >>> comment = CommentFactory(post=post, content='커스텀 댓글')
    """

    class Meta:
        model = Comment

    post = factory.SubFactory(PostFactory)
    content = factory.Faker('sentence', locale='ko_KR')
    user_name = factory.Faker('name', locale='ko_KR')
    user_id = factory.Sequence(lambda n: f'commenter-{n:03d}')
    user_compname = factory.Faker('company', locale='ko_KR')
    user_deptname = factory.LazyFunction(lambda: '지원팀')


class PrivatePostFactory(PostFactory):
    """비밀글 팩토리.

    Example:
        >>> private_post = PrivatePostFactory()
        >>> private_post = PrivatePostFactory(user_id='specific-user')
    """

    is_private = True


class ResolvedPostFactory(PostFactory):
    """해결된 게시글 팩토리.

    Example:
        >>> resolved_post = ResolvedPostFactory()
    """

    is_resolved = True
