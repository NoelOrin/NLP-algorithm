from models.weibo_comment import WeiboComment
from orm.client import ORM


def weibo_blog_comments(id: str):
    """根据ID获取微博博客评论"""
    with ORM() as db:
        item = db.query(WeiboComment).filter(WeiboComment.bid == id)
        return {
            "data": item
        }

def weibo_blogs_comments(id: list[str]):
    """根据ID获取微博博客评论"""
    with ORM() as db:
        item = db.query(WeiboComment).filter(WeiboComment.bid.in_(id))
        return {
            "data": item
        }