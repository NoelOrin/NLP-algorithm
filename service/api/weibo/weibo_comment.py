from typing import Any, Dict, Optional

from dao.weibo_comment_dao import WeiboCommentDAO


def weibo_comment(id: str) -> Dict[str, Any]:
    """根据ID获取微博评论"""
    comment = WeiboCommentDAO.get_by_id(id)
    return {
        "data": comment
    }

def weibo_comments(
        page: int = 1,
        per_page: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = "created_time",
        order_desc: bool = True
) -> Dict[str, Any]:
    """
    获取分页的微博评论列表

    Args:
        page: 页码
        per_page: 每页数量
        filters: 过滤条件字典
        order_by: 排序字段
        order_desc: 是否降序

    Returns:
        分页结果
    """
    return WeiboCommentDAO.get_paginated(
        page=page,
        per_page=per_page,
        filters=filters,
        order_by=order_by,
        order_desc=order_desc
    )