from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Query
from orm.client import ORM
from models.weibo_blog import WeiboBlog


def Paginator(
    model_class: Any,
    page: int = 1,
    per_page: int = 20,
    filters: Optional[Dict[str, Any]] = None,
    order_by: Optional[str] = None,
    order_desc: bool = False
) -> Dict[str, Any]:
    """
    通用分页器
    
    Args:
        model_class: SQLAlchemy模型类
        page: 页码，从1开始
        per_page: 每页数量
        filters: 过滤条件字典，如 {"screen_name": "用户名"}
        order_by: 排序字段
        order_desc: 是否降序排列
        
    Returns:
        分页结果字典
    """
    with ORM() as db:
        # 构建基础查询
        query: Query = db.query(model_class)
        
        # 应用过滤条件
        if filters:
            for field, value in filters.items():
                if hasattr(model_class, field):
                    query = query.filter(getattr(model_class, field) == value)
        
        # 计算总数
        total_count = query.count()
        
        # 计算总页数
        total_pages = (total_count + per_page - 1) // per_page
        
        # 应用排序
        if order_by and hasattr(model_class, order_by):
            order_field = getattr(model_class, order_by)
            if order_desc:
                query = query.order_by(order_field.desc())
            else:
                query = query.order_by(order_field.asc())
        
        # 计算偏移量
        offset = (page - 1) * per_page
        
        # 获取当前页数据
        items = query.offset(offset).limit(per_page).all()
        
        return {
            "items": items,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total_count": total_count,
                "total_pages": total_pages,
                "has_prev": page > 1,
                "has_next": page < total_pages,
                "prev_page": page - 1 if page > 1 else None,
                "next_page": page + 1 if page < total_pages else None
            }
        }


def get_weibo_blog(id: str):
    """根据ID获取微博博客"""
    with ORM() as db:
        blog = db.get(WeiboBlog, id)
        if blog:
            return blog
        else:
            return {"error": "微博不存在"}

def get_weibo_blogs(
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

