import pytest
from postv1.models import User, Post, Reaction, Comment
from postv1.model_methods import react_to_comment, ReactionType
from .utility_functions import create_user, create_post_data, create_comment


@pytest.fixture
def user_setup():
    create_user(name='user1', url='user1@xyz.com')
    create_user(name='user2', url='user2@xyz.com')


@pytest.fixture
def post_setup():
    create_post_data(content='post1', uname='user1', url="user1@xyz.com")


# react to comment methods
@pytest.mark.django_db
def test_react_to_post_user_dne_exception():
    with pytest.raises(Exception) as e:
        react_to_comment(1, 1, reaction_type=ReactionType.LOL.value)
    assert 'User does not exist' in str(e.value)


@pytest.mark.django_db
def test_react_to_post_reaction_dne_exception(user_setup):
    user = User.objects.get(name='user1')

    with pytest.raises(Exception) as e:
        react_to_comment(user.id, comment_id=1, reaction_type=ReactionType.HAHA.value)

    assert 'Comment does not exist' in str(e.value)


@pytest.mark.django_db
def test_given_reaction_type_exists_reaction(user_setup):
    post = create_post_data(content='post1', uname='user1', url="user1@xyz.com")
    comment = post.comments.get(id=1)

    with pytest.raises(Exception) as e:
        react_to_comment(comment.commented_by.id, comment_id=comment.id, reaction_type='LAUGH')

    assert "Reaction does not exist" in str(e.value)


@pytest.mark.django_db
def test_react_to_post_reaction_not_corresponding_user_post_create_reaction(user_setup, post_setup):
    post = Post.objects.get(content='post1')
    comment = post.comments.get(id=1)

    user2 = User.objects.get(name="user2")

    with pytest.raises(Reaction.DoesNotExist):
        Reaction.objects.get(user=user2)

    react_to_comment(user2.id, comment_id=comment.id, reaction_type=ReactionType.LOL.value)

    r = Reaction.objects.get(user=user2)

    assert r.user.name == "user2"
    assert r.user.profile_pic_url == "user2@xyz.com"
    assert r.reaction == ReactionType.LOL.value


@pytest.mark.django_db
def test_react_to_post_user_cooresponding_post_same_reaction(post_setup):
    post = Post.objects.get(content='post1')
    comment = post.comments.get(id=1)
    user = comment.commented_by
    react_to_comment(user.id, comment.id, ReactionType.WOW.value)
    reactions = comment.reactions.all()

    assert len(reactions) == 0


@pytest.mark.django_db
def test_react_to_post_user_corresponding_post_change_reaction(post_setup):
    post = Post.objects.get(content='post1')
    comment = post.comments.get(id=1)

    user = comment.commented_by

    react_to_comment(user.id, comment.id, ReactionType.HAHA.value)
    r = comment.reactions.get(id=2)

    assert r.reaction == ReactionType.HAHA.value
