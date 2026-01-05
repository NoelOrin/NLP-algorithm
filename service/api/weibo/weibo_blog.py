from typing import Optional, Dict, Any

from dao.weibo_blog_dao import WeiboBlogDAO


def weibo_blog(id: str) -> Dict[str, Any]:
    """根据ID获取微博博客"""
    blog = WeiboBlogDAO.get_by_id(id)
    return {
        "data": blog
    }


def weibo_blogs(
        page: int = 1,
        per_page: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = "created_time",
        order_desc: bool = True
) -> Dict[str, Any]:
    """
    获取分页的微博博客列表

    Args:
        page: 页码
        per_page: 每页数量
        filters: 过滤条件字典
        order_by: 排序字段
        order_desc: 是否降序

    Returns:
        分页结果
    """
    return WeiboBlogDAO.get_paginated(
        page=page,
        per_page=per_page,
        filters=filters,
        order_by=order_by,
        order_desc=order_desc
    )


if __name__ == '__main__':
    print()
