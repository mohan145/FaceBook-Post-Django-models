from postv1.models import User, Post, Reaction, Comment


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

    return post
