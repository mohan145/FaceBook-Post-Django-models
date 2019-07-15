from postv1.model_methods import ReactionType
import pytest
from .utility_functions import create_comment, create_post_data, create_user
from postv1.models import Post


@pytest.fixture
def user_setup():

    create_user(name='user1', url='user1@xyz.com')
    create_user(name='user2', url='user1@xyz.com')
    create_user(name='user3', url='user1@xyz.com')


@pytest.fixture
def post_setup():
    create_post_data(content='post1', uname='user1', url='user1@xyz.com')

    create_post_data(content='post2', uname='user2', url='user2@xyz.com')
    create_post_data(content='post3', uname='user3', url='user3@xyz.com')

    post1 = Post.objects.get(id=1)
    post2 = Post.objects.get(id=2)
    post3 = Post.objects.get(id=3)

    user1 = post1.posted_by
    user2 = post2.posted_by
    user3 = post3.posted_by

    # more positive reactions
    post1.reactions.create(user=user3, reaction=ReactionType.WOW.value)
    post1.reactions.create(user=user2, reaction=ReactionType.SAD.value)

    # equal pos and neg reactions
    post2.reactions.create(user=user1, reaction=ReactionType.WOW.value)
    post2.reactions.create(user=user2, reaction=ReactionType.SAD.value)
    post2.reactions.create(user=user3, reaction=ReactionType.ANGRY.value)

    # more neg reactions
    post3.reactions.create(user=user2, reaction=ReactionType.ANGRY.value)
    post3.reactions.create(user=user3, reaction=ReactionType.SAD.value)
