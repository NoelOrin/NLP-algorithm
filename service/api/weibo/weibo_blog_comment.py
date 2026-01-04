from data_models.weibo_blog import WeiboBlog
from data_models.weibo_comment import WeiboComment
from orm.client import ORM
from sqlalchemy.sql import func


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


def weibo_blog_random(limit: int):
    """随机获取微博+评论"""
    with ORM() as db:
        # 使用JOIN查询同时获取微博和评论，减少数据库查询次数
        items = db.query(WeiboBlog, WeiboComment).outerjoin(
            WeiboComment, WeiboBlog.bid == WeiboComment.bid
        ).order_by(func.random()).limit(limit).all()

        # 将查询结果按照微博分组
        result_map = {}
        for blog, comment in items:
            if blog.bid not in result_map:
                result_map[blog.bid] = {
                    "id": blog.id,
                    "bid": blog.bid,
                    "content": blog.text,
                    "comments": []
                }

            # 如果存在评论，则添加到对应微博的评论列表中
            if comment is not None:
                result_map[blog.bid]["comments"].append({
                    "id": comment.id,
                    "bid": comment.bid,
                    "content": comment.text
                })

        result = list(result_map.values())

        return {
            "weibo": result,
        }

if __name__ == '__main__':
    print(weibo_blog_random(10))