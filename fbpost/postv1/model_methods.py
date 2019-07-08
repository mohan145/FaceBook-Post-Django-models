from .models import User, Reaction, Post, Comment
from django.db.models import Q, Count
from enum import Enum


class ReactionType(Enum):
    LOL = "LOL"
    HAHA = "HAHA"
    WOW = "WOW"
    LIKE = "LIKE"
    SAD = "SAD"
    ANGRY = " ANGRY"
    LOVE = "LOVE"


def create_post(user_id, post_content):
    user = User.objects.get(id=user_id)
    post = user.posts.create(content=post_content)
    return post.id


def get_user_data(user):
    user_data = {}
    user_data.update({"name": user.name})
    user_data.update({"user_id": user.id})
    user_data.update({"profile_pic_url": user.profile_pic_url})

    return user_data


def get_reactions_data(obj):
    reaction_data = {}
    reaction_data.update({"count": obj.reactions.count()})
    types = obj.reactions.values_list('reaction', flat=True).distinct()
    reaction_data.update({"type": list(types)})

    return reaction_data


def get_post(post_id):
    result = dict()

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        raise Exception("User not found")

    result.update({"posted_id": post_id})
    result.update({"posted_at": post.posted_at.strftime("%Y-%m-%d %H:%M:%S.%f")})
    result.update({"post_content": post.content})

    # fetching user data
    user = User.objects.get(id=post.posted_by.id)
    user_data = get_user_data(user)
    result.update({"posted_by": user_data})

    # fetching reactions data
    reaction_data = get_reactions_data(post)
    result.update({"reactions": reaction_data})

    # getting comments
    comments = post.comments.all()
    comments_result = get_comments(comments)

    result.update({"comments": comments_result})
    result.update({"comments_count": post.comments.count()})

    return result


def get_comments(comments):
    res_list = list()

    for comment in comments:
        res_dict = dict()
        res_dict.update({"comment_id": comment.id})

        # user data
        user = User.objects.get(id=comment.commented_by.id)
        user_data = get_user_data(user)

        res_dict.update({"commenter": user_data})
        res_dict.update({"commented_at": comment.commented_at.strftime("%Y-%m-%d %H:%M:%S.%f")})
        res_dict.update({"comment_content:": comment.content})

        # fetching reactions data
        reaction_data = get_reactions_data(comment)
        res_dict.update({"reactions": reaction_data})

        # handling comments and replies for same function
        temp = get_comments(comment.replies.all())

        if temp != None:
            res_dict.update({"replies count": comment.replies.count()})
            res_dict.update({"replies": temp})

        res_list.append(res_dict)

        return res_list


def get_user_posts(user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise Exception("User not found")
    posts = user.posts.all()

    result = list()

    for post in posts:
        result.append(get_post(post.id))

    return result


def delete_post(post_id):
    try:
        post_to_delete = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        raise Exception("Post not Found")
    post_to_delete.delete()


def react_to_post(user_id, post_id, reaction_type):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise Exception("User does not exist")

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        raise Exception("Post does not exist")

    reactions_list = [ReactionType.LOL.value, ReactionType.HAHA.value
        , ReactionType.WOW.value, ReactionType.LIKE.value
        , ReactionType.LOVE.value,
                      ReactionType.SAD.value, ReactionType.ANGRY.value]

    if reaction_type not in reactions_list:
        raise Exception("Reaction does not exist")

    try:
        react = Reaction.objects.get(user_id=user.id, post_id=post.id)
        if react.reaction == reaction_type:
            react.delete()
        else:
            react.reaction = reaction_type
            react.save()

    except:

        Reaction.objects.create(user=user, reaction=reaction_type, post=post)


def get_posts_reacted_by_user(user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise Exception("User does not exist")

    reactions = user.reactions.all()

    posts_data = list()

    for reaction in reactions:
        posts_data.append(get_post(reaction.post.id))

    return posts_data


def get_reactions_to_post(post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        raise Exception("Post does not exist")

    reactions = post.reactions.all()

    result = []

    for obj in reactions:
        data = {}

        data.update({"user_id": obj.user.id})
        data.update({"name": obj.user.name})
        data.update({"profile_pic": obj.user.profile_pic_url})

        data.update({"reaction": obj.reaction})

        result.append(data)

    return result


def get_reaction_metrics(post_id):
    try:
        Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        raise Exception("Post does not exist")

    count_object = Count('reaction')

    temp = Reaction.objects.filter(post_id=19).values('reaction').annotate(count=count_object)

    return list(temp)


def get_posts_with_more_positive_reactions():
    pos_reactions = [ReactionType.LOL.value, ReactionType.HAHA.value
        , ReactionType.WOW.value, ReactionType.LIKE.value
        , ReactionType.LOVE.value]

    neg_reactions = [ReactionType.SAD.value, ReactionType.ANGRY.value]



    res_post_ids = list()

    pos_r = Count('reaction', filter=Q(reaction__in=pos_reactions))
    neg_r = Count('reaction', filter=Q(reaction__in=neg_reactions))

    check_count = Reaction.objects.exclude(post=None).values('post_id').annotate(pos_reac=pos_r).annotate(
        neg_reac=neg_r)

    for x in check_count:

        if x['pos_reac'] > x['neg_reac']:
            res_post_ids.append(x['post_id'])

    return res_post_ids


# comment methods

def add_comment(post_id, comment_user_id, comment_text):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        raise Exception("Post doesnot Exists")

    try:
        user = User.objects.get(id=comment_user_id)
    except User.DoesNotExist:
        raise Exception("User doesnot Exists")

    created_comment = Comment.objects.create(content=comment_text, commented_by=user, post=post)

    return created_comment.id


def react_to_comment(user_id, comment_id, reaction_type):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise Exception("User does not exist")

    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        raise Exception("Comment does not exist")

    reactions_list = [ReactionType.LOL.value, ReactionType.HAHA.value
        , ReactionType.WOW.value, ReactionType.LIKE.value
        , ReactionType.LOVE.value,
                      ReactionType.SAD.value, ReactionType.ANGRY.value]

    if reaction_type not in reactions_list:
        raise Exception("Reaction does not exist")

    try:
        react = Reaction.objects.get(user_id=user.id, comment_id=comment.id)
        if react.reaction == reaction_type:
            react.delete()
        else:
            react.reaction = reaction_type
            react.save()

    except:

        Reaction.objects.create(user=user, reaction=reaction_type, comment=comment)


# replies methods

def reply_to_comment(comment_id, reply_user_id, reply_text):
    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        raise Exception("Comment doesnot Exists")

    try:
        user = User.objects.get(id=reply_user_id)
    except User.DoesNotExist:
        raise Exception("User doesnot Exists")

    reply_comment = Comment.objects.create(content=reply_text, commented_by=user, parent_comment=comment)

    return reply_comment.id


def get_replies_for_comment(comment_id):
    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        raise Exception("Comment doesnot Exists")

    if comment.parent_comment is not None:
        raise Exception("The given comment is a reply")

    replies = comment.replies.all()

    result = get_comments(replies)

    return result


if __name__ == '__main__':
    get_post(1)
