from .models import User, Reaction, Post, Comment
from django.db.models import Q, Count, F
from enum import Enum
from django.db import connection
from django.db.models import Prefetch


class ReactionType(Enum):
    LOL = "LOL"
    HAHA = "HAHA"
    WOW = "WOW"
    LIKE = "LIKE"
    SAD = "SAD"
    ANGRY = "ANGRY"
    LOVE = "LOVE"


def create_post(user_id, post_content):
    # done opt
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise Exception("User Does not Exist")

    post = user.posts.create(content=post_content)
    return post.id


def get_user_data(user):
    # done
    user_data = {}
    user_data.update({"name": user.name})
    user_data.update({"user_id": user.id})
    user_data.update({"profile_pic_url": user.profile_pic_url})

    return user_data


def get_reactions_data(reactions):
    # done
    reaction_data = {}
    reaction_data.update({"count": len(reactions)})

    # types = reactions.values_list('reaction', flat=True).distinct()

    reaction_list = []
    for reaction in reactions:
        reaction_list.append(reaction.reaction)

    reaction_list = list(set(reaction_list))
    reaction_data.update({"type": reaction_list})
    # reaction_data.update({"type": list(types)})

    return reaction_data


def get_comment(comment):
    res_dict = dict()
    res_dict.update({"comment_id": comment.id})

    # user data
    # user = User.objects.get(id=comment.commented_by.id)

    user_data = get_user_data(comment.commented_by)

    res_dict.update({"commenter": user_data})
    res_dict.update({"commented_at": comment.commented_at.strftime("%Y-%m-%d %H:%M:%S.%f")})

    res_dict.update({"comment_content:": comment.content})

    # fetching reactions data

    reaction_data = get_reactions_data(comment.reactions.all())
    res_dict.update({"reactions": reaction_data})

    if comment.post is not None:
        res_dict.update({'replies_count': len(comment.replies.all())})

        replies_list = list()

        for reply in comment.replies.all():
            reply_data = get_comment(reply)

            replies_list.append(reply_data)

        res_dict.update({'replies': replies_list})

    return res_dict


def get_post(post_id):
    # done

    result = dict()
    try:
        post = Post.objects.select_related('posted_by').prefetch_related(
            Prefetch('comments', queryset=Comment.objects.select_related('commented_by').
                     prefetch_related(Prefetch('replies',
                                               queryset=Comment.objects.select_related('commented_by').prefetch_related(
                                                   Prefetch('reactions', queryset=Reaction.objects.select_related(
                                                       'user')))),

                                      Prefetch('reactions',
                                               queryset=Reaction.objects.select_related(
                                                   'user'))

                                      ))

            , Prefetch('reactions', queryset=Reaction.objects.select_related('user'))).get(id=post_id)

    except Post.DoesNotExist:

        raise Exception("Post Does not Exist")

    result.update({"posted_id": post_id})
    result.update({"posted_at": post.posted_at.strftime("%Y-%m-%d %H:%M:%S.%f")})
    result.update({"post_content": post.content})

    # fetching user data
    user_data = get_user_data(post.posted_by)
    result.update({"posted_by": user_data})

    # fetching reactions data
    reactions = post.reactions.all()
    reaction_data = get_reactions_data(reactions)
    result.update({"reactions": reaction_data})

    comments_list = list()
    # getting comments

    for comment in post.comments.all():
        comment_data = get_comment(comment)
        comments_list.append(comment_data)

    result.update({"comments": comments_list})
    result.update({"comments_count": len(post.comments.all())})

    return result


def get_post_custom(post):
    result = dict()

    result.update({"posted_id": post.id})
    result.update({"posted_at": post.posted_at.strftime("%Y-%m-%d %H:%M:%S.%f")})
    result.update({"post_content": post.content})

    # fetching user data
    user_data = get_user_data(post.posted_by)
    result.update({"posted_by": user_data})

    # fetching reactions data
    reactions = post.reactions.all()
    reaction_data = get_reactions_data(reactions)
    result.update({"reactions": reaction_data})

    comments_list = list()
    # getting comments
    for comment in post.comments.all():
        comment_data = get_comment(comment)
        comments_list.append(comment_data)

    result.update({"comments": comments_list})
    result.update({"comments_count": len(post.comments.all())})

    return result


def get_user_posts(user_id):
    # done
    try:

        user = User.objects.prefetch_related(Prefetch('posts', queryset=Post.objects.select_related(
            'posted_by').prefetch_related(Prefetch('comments', queryset=Comment.objects.select_related('commented_by').
                                                   prefetch_related(Prefetch('replies',
                                                                             queryset=Comment.objects.select_related(
                                                                                 'commented_by').prefetch_related(
                                                                                 Prefetch('reactions',
                                                                                          queryset=Reaction.objects.select_related(
                                                                                              'user')))),

                                                                    Prefetch('reactions',
                                                                             queryset=Reaction.objects.select_related(
                                                                                 'user'))

                                                                    ))

                                          , Prefetch('reactions',
                                                     queryset=Reaction.objects.select_related('user'))))).get(
            id=user_id)

    except User.DoesNotExist:
        raise Exception("User not found")

    result = list()

    for post in user.posts.all():
        result.append(get_post_custom(post))

    return result


def delete_post(post_id):
    # done
    Post.objects.filter(id=post_id).delete()


def react_to_post(user_id, post_id, reaction_type):
    # done
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

    except Exception:

        Reaction.objects.create(user=user, reaction=reaction_type, post=post)


def get_posts_reacted_by_user(user_id):
    # done
    try:
        user = User.objects.prefetch_related(
            Prefetch('reactions', queryset=Reaction.objects.select_related('post'))).get(id=user_id)
    except User.DoesNotExist:
        raise Exception("User does not exist")

    post_ids = user.reactions.values('post__id')

    posts_data = list()

    posts = Post.objects.select_related('posted_by').prefetch_related(
        Prefetch('comments', queryset=Comment.objects.select_related('commented_by').
                 prefetch_related(Prefetch('replies',
                                           queryset=Comment.objects.select_related('commented_by').prefetch_related(
                                               Prefetch('reactions', queryset=Reaction.objects.select_related(
                                                   'user')))),

                                  Prefetch('reactions',
                                           queryset=Reaction.objects.select_related(
                                               'user'))

                                  ))

        , Prefetch('reactions', queryset=Reaction.objects.select_related('user'))).filter(id__in=post_ids)

    for post in posts:
        posts_data.append(get_post_custom(post))

    return posts_data


def get_reactions_to_post(post_id):
    # done
    try:
        post = Post.objects.prefetch_related('reactions', 'reactions__user').get(id=post_id)
    except Post.DoesNotExist:
        raise Exception("Post does not exist")

    result = []

    for obj in post.reactions.all():
        temp = get_user_data(obj.user)
        temp.update({"reaction": obj.reaction})

        result.append(temp)

    return result


def get_reaction_metrics(post_id):
    # done
    try:

        Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        raise Exception("Post does not exist")

    count_object = Count('reaction')

    temp = Reaction.objects.filter(post_id=post_id).values('reaction').annotate(count=count_object)

    return list(temp)


def get_posts_with_more_positive_reactions():
    # done
    pos_reactions = [ReactionType.LOL.value, ReactionType.HAHA.value
        , ReactionType.WOW.value, ReactionType.LIKE.value
        , ReactionType.LOVE.value]

    neg_reactions = [ReactionType.SAD.value, ReactionType.ANGRY.value]

    pos_r = Count('reaction', filter=Q(reaction__in=pos_reactions))
    neg_r = Count('reaction', filter=Q(reaction__in=neg_reactions))

    res_post_ids = Reaction.objects.exclude(post=None).values('post_id').annotate(pos_reac=pos_r).annotate(
        neg_reac=neg_r).filter(pos_reac__gt=F('neg_reac')).values_list('post_id', flat=True)

    return list(res_post_ids)


# comment methods

def add_comment(post_id, comment_user_id, comment_text):
    # done
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
    # done
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
        react = Reaction.objects.get(user_id=user_id, comment_id=comment_id)
        if react.reaction == reaction_type:
            react.delete()
        else:
            react.reaction = reaction_type
            react.save()
    except:

        Reaction.objects.create(user=user, reaction=reaction_type, comment=comment)


# replies methods

def reply_to_comment(comment_id, reply_user_id, reply_text):
    # done
    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        raise Exception("Comment doesnot Exists")

    try:
        u = User.objects.get(id=reply_user_id)
    except User.DoesNotExist:
        raise Exception("User doesnot Exists")

    # handling if given reply_id case
    if comment.parent_comment is not None:
        reply_comment = Comment.objects.create(content=reply_text, commented_by=u,
                                               parent_comment=comment.parent_comment)
        return reply_comment.id

    reply_comment = Comment.objects.create(content=reply_text, commented_by=u, parent_comment=comment)

    return reply_comment.id


def get_replies_for_comment(comment_id):
    try:

        comment = Comment.objects.prefetch_related(Prefetch('replies', queryset=Comment.objects.select_related(
            'commented_by').prefetch_related(Prefetch('reactions', queryset=Reaction.objects.select_related(
            'user')))),
                                                   Prefetch('reactions',
                                                            queryset=Reaction.objects.select_related(
                                                                'user'))

                                                   ).get(id=comment_id)

    except Comment.DoesNotExist:
        raise Exception("Comment does not Exists")

    if comment.parent_comment is not None:
        raise Exception("The given comment is a reply")

    replies_list = list()
    for reply in comment.replies.all():
        result = get_comment(reply)

        replies_list.append(result)

    return replies_list
