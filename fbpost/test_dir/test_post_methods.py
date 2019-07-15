import pytest
from postv1.models import User, Post, Reaction, Comment
from postv1.model_methods import create_post, get_post, react_to_post, ReactionType, get_reaction_metrics


def create_user(name, url):
    user = User.objects.create(name=name, profile_pic_url=url)
    return user


def create_comment(uname, url, content):
    user = create_user(uname, url)
    comment = Comment.objects.create(commented_by=user, content=content)
    return comment


def create_post_data(content, uname, url):
    user = create_user(uname, url)
    post = Post.objects.create(content=content, posted_by=user)
    post.reactions.create(reaction='LIKE', user=user)
    post.comments.create(commented_by=user, content='comment1')

    post.comments.all()[0].reactions.create(user=user, reaction='WOW')
    post.comments.all()[0].replies.create(commented_by=user, content="reply1")
    post.comments.all()[0].replies.all()[0].reactions.create(user=user, reaction='HAHA')


@pytest.fixture
def user_setup():
    # User.objects.create(name='user1', profile_pic_url="user1@xyz.com")
    create_user(name='user1', url='user1@xyz.com')


@pytest.fixture
def post_setup():
    create_post_data(content='post1', uname='user1', url='user1@xyz.com')


# create post test
@pytest.mark.django_db
def test_create_post_user_dne_exception():
    with pytest.raises(Exception) as e:
        create_post("1", "post1")
    assert "User Does not Exist" in str(e.value)


@pytest.mark.django_db
def test_create_post_check_post_post_id(user_setup):
    post_content = "post 1"

    user = User.objects.get(name='user1')
    returned_post_id = create_post(user.id, post_content=post_content)
    created_post = Post.objects.get(id=returned_post_id)

    assert returned_post_id == created_post.id
    assert post_content in created_post.content
    assert created_post.posted_by == user


# get post test
@pytest.mark.django_db
def test_get_post_post_dne_exception():
    with pytest.raises(Exception) as e:
        get_post(1)
    assert "Post Does not Exist" in str(e.value)


@pytest.mark.django_db
def test_get_post_post_data(post_setup):
    p = Post.objects.get(content="post1")
    returned_post = get_post(p.id)

    # TODO: Refactor below code
    assert returned_post['post_content'] == "post1"
    assert returned_post['posted_by']['name'] == "user1"
    assert returned_post['posted_by']['profile_pic_url'] == "user1@xyz.com"
    assert returned_post['reactions']['count'] == 1
    assert returned_post['reactions']['type'][0] == 'LIKE'
    assert returned_post['comments_count'] == 1
    assert returned_post['comments'][0]['comment_content:'] == "comment1"
    assert returned_post['comments'][0]['reactions']['count'] == 1
    assert returned_post['comments'][0]['reactions']['type'] == ['WOW']

    assert returned_post['comments'][0]['replies_count'] == 1

    assert returned_post['comments'][0]['replies'][0]['comment_content:'] == 'reply1'
    assert returned_post['comments'][0]['replies'][0]['reactions']['count'] == 1
    assert returned_post['comments'][0]['replies'][0]['reactions']['type'][0] == 'HAHA'


# react to post methods
@pytest.mark.django_db
def test_react_to_post_user_dne_exception():
    with pytest.raises(Exception) as e:
        react_to_post(1, 1, reaction_type=ReactionType.LOL.value)
    assert 'User does not exist' in str(e.value)


@pytest.mark.django_db
def test_react_to_post_reaction_dne_exception(user_setup):
    user = User.objects.get(name='user1')

    with pytest.raises(Exception) as e:
        react_to_post(user.id, post_id=1, reaction_type='LOL')
        print(e.value)
    assert 'Post does not exist' in str(e.value)


@pytest.mark.django_db
def test_given_reaction_type_exists_reaction(post_setup):
    u = create_user('mohan', 'mohan@xyz.com')
    p = Post.objects.all()[0]

    with pytest.raises(Exception) as e:
        react_to_post(u.id, post_id=p.id, reaction_type='LAUGH')

    assert "Reaction does not exist" in str(e.value)


@pytest.mark.django_db
def test_react_to_post_reaction_not_corresponding_user_post_create_reaction():
    u1 = create_user('kmk', 'xyz.com')
    post = Post.objects.create(posted_by=u1, content="post1")
    u2 = create_user('mohan', 'mohan@xyz.com')

    with pytest.raises(Reaction.DoesNotExist):
        Reaction.objects.get(user=u2)

    react_to_post(u2.id, post_id=post.id, reaction_type=ReactionType.LOL.value)

    r = Reaction.objects.get(user=u2)

    assert r.user.name == "mohan"
    assert r.user.profile_pic_url == "mohan@xyz.com"
    assert r.reaction == ReactionType.LOL.value


@pytest.mark.django_db
def test_react_to_post_user_cooresponding_post_same_reaction():
    u1 = create_user('kmk', 'xyz.com')
    post = Post.objects.create(posted_by=u1, content="post1")
    post.reactions.create(user=u1, reaction=ReactionType.HAHA.value)

    react_to_post(u1.id, post.id, ReactionType.HAHA.value)
    reactions = Reaction.objects.all()
    assert len(reactions) == 0


@pytest.mark.django_db
def test_react_to_post_user_corresponding_post_change_reaction():
    u1 = create_user('kmk', 'xyz.com')
    post = Post.objects.create(posted_by=u1, content="post1")
    post.reactions.create(user=u1, reaction=ReactionType.HAHA.value)

    react_to_post(u1.id, post.id, ReactionType.WOW.value)
    r = Reaction.objects.get(post=post.id)

    assert r.reaction == ReactionType.WOW.value


# test reaction metrics
@pytest.mark.django_db
def test_reaction_metrics_post_exists(post_setup):
    with pytest.raises(Exception) as e:
        get_reaction_metrics(post_id=2)
    assert "Post does not exist" in str(e.value)


@pytest.mark.django_db
def test_post_reaction_metrics_metrics_data(post_setup, user_setup):
    post = Post.objects.get(id=1)
    user = post.posted_by
    user2 = User.objects.get(id=2)
    post.reactions.create(user=user, reaction=ReactionType.LIKE.value)
    post.reactions.create(user=user2, reaction=ReactionType.HAHA.value)
    post.reactions.create(user=user2, reaction=ReactionType.SAD.value)

    res = get_reaction_metrics(1)

    assert {'reaction': ReactionType.HAHA.value, 'count': 1} in res
    assert {'reaction': ReactionType.LIKE.value, 'count': 2} in res
    assert {'reaction': ReactionType.SAD.value, 'count': 1} in res


