import pytest
from postv1.models import User, Post, Reaction, Comment
from postv1.model_methods import get_posts_with_more_positive_reactions, create_post, get_post, react_to_post, \
    ReactionType, get_reaction_metrics, delete_post, get_reactions_to_post
from .utility_functions import create_user, create_post_data, create_comment


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
    assert returned_post['post_content'] == p.content
    assert returned_post['posted_by']['name'] == p.posted_by.name
    assert returned_post['posted_by']['profile_pic_url'] == p.posted_by.profile_pic_url
    assert returned_post['reactions']['count'] == 3
    assert ReactionType.LIKE.value in returned_post['reactions']['type']
    assert ReactionType.WOW.value in returned_post['reactions']['type']
    assert ReactionType.SAD.value in returned_post['reactions']['type']

    assert returned_post['comments_count'] == 1
    assert returned_post['comments'][0]['comment_content:'] == "comment1"
    assert returned_post['comments'][0]['reactions']['count'] == 1
    assert returned_post['comments'][0]['reactions']['type'] == [ReactionType.WOW.value]

    assert returned_post['comments'][0]['replies_count'] == 1

    assert returned_post['comments'][0]['replies'][0]['comment_content:'] == 'reply1'
    assert returned_post['comments'][0]['replies'][0]['reactions']['count'] == 1
    assert returned_post['comments'][0]['replies'][0]['reactions']['type'][0] == ReactionType.HAHA.value


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
        react_to_post(user.id, post_id=1, reaction_type=ReactionType.LOL.value)
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
        get_reaction_metrics(post_id=9)
    assert "Post Does not Exist" in str(e.value)


@pytest.mark.django_db
def test_post_reaction_metrics_metrics_data(post_setup, user_setup):
    res = get_reaction_metrics(1)

    assert len(res) == 3
    assert {'reaction': ReactionType.WOW.value, 'count': 1} in res
    assert {'reaction': ReactionType.LIKE.value, 'count': 1} in res
    assert {'reaction': ReactionType.SAD.value, 'count': 1} in res


# get post with more postive reactions test
@pytest.mark.django_db
def test_post_with_more_pos_reactions(post_setup, user_setup):
    post1 = Post.objects.get(id=1)
    result = get_posts_with_more_positive_reactions()

    assert Post.objects.get(id=result[0]) == post1


# delete post test
@pytest.mark.django_db
def test_delete_post(post_setup):
    post_to_delete = Post.objects.get(id=3)

    delete_post(post_to_delete.id)

    with pytest.raises(Exception) as e:
        get_post(3)
    assert "Post Does not Exist" in str(e.value)


# get reactions to post tests
@pytest.mark.django_db
def test_get_reactions_to_post_post_exception():
    with pytest.raises(Exception) as e:
        get_reactions_to_post(1)
    assert "Post Does not Exist" in str(e.value)


@pytest.mark.django_db
def test_get_reactions_to_post_reactions_data(post_setup):
    post = Post.objects.get(id=1)

    res = get_reactions_to_post(1)

    assert len(res) == 3

    user1 = post.reactions.get(reaction=ReactionType.LIKE.value).user
    user2 = post.reactions.get(reaction=ReactionType.WOW.value).user
    user3 = post.reactions.get(reaction=ReactionType.SAD.value).user

    users = [{"LIKE": user1}, {"WOW": user2}, {"SAD": user3}]
    for u in users:
        for reaction, user in u.items():
            assert {'name': user.name, 'user_id': user.id, 'profile_pic_url': user.profile_pic_url,
                    'reaction': reaction} in res
