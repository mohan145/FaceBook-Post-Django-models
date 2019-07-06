from .models import User, Reaction, Post, Comment


def create_post(user_id, post_content):
    user = User.objects.get(id=user_id)

    post_id = user.posts.create(content=post_content)

    return post_id


def get_post(post_id):
    result = dict()

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        raise Exception("User not found")

    result.update({"posted_id": post_id})

    result.update({"posted_at": str(post.posted_at)[:len(str(post.posted_at)) - 6]})

    result.update({"post_content": post.content})

    reactionslist = []

    # fetching user data
    userdata = {}

    userdata.update({"name": post.posted_by.name})
    userdata.update({"user_id": post.posted_by.id})
    userdata.update({"profile_pic_url": post.posted_by.profile_pic_url})

    result.update({"posted_by": userdata})

    # fetching reactions data

    for x in post.reactions.all():
        reactionslist.append(x.reaction)

    reactiondata = {}
    reactiondata.update({"count": len(reactionslist)})
    reactiondata.update({"type": list(set(reactionslist))})

    result.update({"reactions": reactiondata})

    # getting comments
    comments = post.comments.all()
    comments_result = get_comments(comments)

    result.update({"comments": comments_result})

    result.update({"comments_count": post.comments.count()})



    return result


# custom method to get comments for a post
def get_comments(comments):
    res_list = list()

    for x in comments:
        res_dict = dict()

        res_dict.update({"comment_id": x.id})

        user_data = dict()
        user_data.update({"user_id": x.commented_by.id})
        user_data.update({"name": x.commented_by.name})
        user_data.update({"profile_pic_url": x.commented_by.profile_pic_url})

        res_dict.update({"commenter": user_data})
        res_dict.update({"commented_at": str(x.commented_at)[:len(str(x.commented_at)) - 6]})
        res_dict.update({"comment_content:": x.content})

        reactionslist = []
        # fetching reactions data

        for c in x.reactions.all():
            reactionslist.append(c.reaction)

        reactiondata = {}
        reactiondata.update({"count": x.reactions.count()})
        reactiondata.update({"type": list(set(reactionslist))})

        res_dict.update({"reactions": reactiondata})

        res_list.append(res_dict)

    # print(res_list)

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
        u = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise Exception("User does not exist")

    try:
        p = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        raise Exception("Post does not exist")

    if reaction_type not in ["HAHA", "WOW", "LIKE", "LOVE", "SAD"]:
        raise Exception("Reaction does not exist")

    try:
        react = Reaction.objects.get(user_id=u.id, post_id=p.id)
        if react.reaction == reaction_type:
            react.delete()
        else:
            react.reaction = reaction_type
            react.save()

    except:

        Reaction.objects.create(user=u, reaction=reaction_type, post=p)


def get_posts_reacted_by_user(user_id):
    try:
        u = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise Exception("User does not exist")

    reactions = u.reactions.all()

    postsdata = list()

    for x in reactions:
        postsdata.append(get_post(x.post.id))

    return postsdata


def get_reactions_to_post(post_id):
    try:
        p = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        raise Exception("Post does not exist")

    reactions = p.reactions.all()

    result = []

    for x in reactions:
        temp = {}

        temp.update({"user_id": x.user.id})
        temp.update({"name": x.user.name})
        temp.update({"profile_pic": x.user.profile_pic_url})

        temp.update({"reaction": x.reaction})

        result.append(temp)

    return result


def get_reaction_metrics(post_id):
    try:
        p = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        raise Exception("Post does not exist")

    reactions = p.reactions.all()

    reaction_metrics = list()

    metrics = {}

    for x in reactions:

        if x.reaction in metrics.keys():
            metrics[x.reaction] += 1
        else:
            metrics[x.reaction] = 1

    for key, values in metrics.items():
        temp = {}
        temp.update({"reaction_type": key})
        temp.update({"count": values})

        reaction_metrics.append(temp)

    print(reaction_metrics)


def get_posts_with_more_positive_reactions():
    pos = ["LIKE", "WOW", "LOVE", "HAHA"]
    negs = ["SAD", "ANGRY"]

    res_post_ids = list()

    for p in Post.objects.all():

        # print(p)
        reactions = p.reactions.all()

        check_count = list((0, 0))
        # print(reactions)

        for r in reactions:

            if r.reaction in pos:
                check_count[0] += 1
            if r.reaction in negs:
                check_count[1] += 1

        if check_count[0] > check_count[1]:
            res_post_ids.append(p.id)
        # print("_______________")

    return res_post_ids


# comment methods

def add_comment(post_id, comment_user_id, comment_text):
    try:
        p = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        raise Exception("Post doesnot Exists")

    try:
        u = User.objects.get(id=comment_user_id)
    except User.DoesNotExist:
        raise Exception("User doesnot Exists")

    c = Comment.objects.create(content=comment_text, commented_by=u, post=p)

    return c.id


def react_to_comment(user_id, comment_id, reaction_type):
    try:
        u = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise Exception("User does not exist")

    try:
        c = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        raise Exception("Comment does not exist")

    if reaction_type not in ["HAHA", "WOW", "LIKE", "LOVE", "SAD"]:
        raise Exception("Reaction does not exist")

    try:
        react = Reaction.objects.get(user_id=u.id, comment_id=c.id)
        if react.reaction == reaction_type:
            react.delete()
        else:
            react.reaction = reaction_type
            react.save()

    except:

        Reaction.objects.create(user=u, reaction=reaction_type, comment=c)


# replies methods

def reply_to_comment(comment_id, reply_user_id, reply_text):
    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        raise Exception("Comment doesnot Exists")

    try:
        u = User.objects.get(id=reply_user_id)
    except User.DoesNotExist:
        raise Exception("User doesnot Exists")

    reply_comment = Comment.objects.create(content=reply_text, commented_by=u, parent_comment=comment)

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

    # print(result)


if __name__ == '__main__':
    get_post(1)
