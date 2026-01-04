from typing import Optional, Dict, Any
from data_models.weibo_blog import WeiboBlog
from data_models.weibo_comment import WeiboComment
from orm.client import ORM
from utils.paginator import Paginator
from sqlalchemy.sql import func


def weibo_blog(id: str):
    """根据ID获取微博博客"""
    with ORM() as db:
        item = db.query(WeiboBlog).filter(WeiboBlog.id == id)
        return {
            "data": item
        }


def weibo_blogs(
        page: int = 1,
        per_page: int = 20,
        screen_name: Optional[str] = None,
        order_by: Optional[str] = "created_time",
        order_desc: bool = True
) -> Dict[str, Any]:
    """
    获取分页的微博博客列表

    Args:
        page: 页码
        per_page: 每页数量
        screen_name: 用户名过滤
        order_by: 排序字段
        order_desc: 是否降序

    Returns:
        分页结果
    """
    filters = {}
    if screen_name:
        filters["screen_name"] = screen_name

    return Paginator(
        model_class=WeiboBlog,
        page=page,
        per_page=per_page,
        filters=filters,
        order_by=order_by,
        order_desc=order_desc
    )


if __name__ == '__main__':
    print()
