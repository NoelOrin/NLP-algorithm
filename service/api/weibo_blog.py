from orm.client import ORM
from models.weibo_blog import WeiboBlog

def get_weibo_blog(id: str):
    """根据ID获取微博博客"""
    with ORM() as db:
        blog = db.get(WeiboBlog, id)
        if blog:
            return blog
        else:
            return {"error": "微博博客不存在"}


def get_weibo_blogs(ids: list[str]):
    """根据ID列表获取微博博客"""
    with ORM() as db:
        blogs = db.query(WeiboBlog).filter(WeiboBlog.id.in_(ids)).all()
        return blogs

