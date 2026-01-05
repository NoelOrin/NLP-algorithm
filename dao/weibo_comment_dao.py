from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Query

from data_models.weibo_comment import WeiboComment
from orm.client import ORM


class WeiboCommentDAO:
    """微博评论数据访问对象"""
    
    @staticmethod
    def get_by_id(comment_id: str) -> Optional[WeiboComment]:
        """根据ID获取微博评论"""
        with ORM() as db:
            return db.query(WeiboComment).filter(WeiboComment.id == comment_id).first()
    
    @staticmethod
    def get_by_ids(comment_ids: List[str]) -> List[WeiboComment]:
        """根据ID列表获取微博评论列表"""
        with ORM() as db:
            return db.query(WeiboComment).filter(WeiboComment.id.in_(comment_ids)).all()
    
    @staticmethod
    def get_by_blog_id(blog_id: str) -> List[WeiboComment]:
        """根据博客ID获取评论列表"""
        with ORM() as db:
            return db.query(WeiboComment).filter(WeiboComment.bid == blog_id).all()
    
    @staticmethod
    def get_by_blog_ids(blog_ids: List[str]) -> List[WeiboComment]:
        """根据博客ID列表获取评论列表"""
        with ORM() as db:
            return db.query(WeiboComment).filter(WeiboComment.bid.in_(blog_ids)).all()
    
    @staticmethod
    def get_all() -> List[WeiboComment]:
        """获取所有微博评论"""
        with ORM() as db:
            return db.query(WeiboComment).all()
    
    @staticmethod
    def count() -> int:
        """获取微博评论总数"""
        with ORM() as db:
            return db.query(WeiboComment).count()
    
    @staticmethod
    def count_by_blog_id(blog_id: str) -> int:
        """根据博客ID获取评论数量"""
        with ORM() as db:
            return db.query(WeiboComment).filter(WeiboComment.bid == blog_id).count()
    
    @staticmethod
    def get_paginated(
        page: int = 1,
        per_page: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        order_desc: bool = False
    ) -> Dict[str, Any]:
        """
        获取分页的微博评论列表
        
        Args:
            page: 页码
            per_page: 每页数量
            filters: 过滤条件字典
            order_by: 排序字段
            order_desc: 是否降序排列
            
        Returns:
            分页结果字典
        """
        with ORM() as db:
            query: Query = db.query(WeiboComment)
            
            # 应用过滤条件
            if filters:
                for field, value in filters.items():
                    if hasattr(WeiboComment, field):
                        query = query.filter(getattr(WeiboComment, field) == value)
            
            # 计算总数
            total_count = query.count()
            total_pages = (total_count + per_page - 1) // per_page
            
            # 应用排序
            if order_by and hasattr(WeiboComment, order_by):
                order_field = getattr(WeiboComment, order_by)
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
    
    @staticmethod
    def create(comment_data: Dict[str, Any]) -> WeiboComment:
        """创建微博评论"""
        with ORM() as db:
            comment = WeiboComment(**comment_data)
            db.add(comment)
            db.commit()
            db.refresh(comment)
            return comment
    
    @staticmethod
    def update(comment_id: str, update_data: Dict[str, Any]) -> Optional[WeiboComment]:
        """更新微博评论"""
        with ORM() as db:
            comment = db.query(WeiboComment).filter(WeiboComment.id == comment_id).first()
            if comment:
                for key, value in update_data.items():
                    if hasattr(comment, key):
                        setattr(comment, key, value)
                db.commit()
                db.refresh(comment)
            return comment
    
    @staticmethod
    def delete(comment_id: str) -> bool:
        """删除微博评论"""
        with ORM() as db:
            comment = db.query(WeiboComment).filter(WeiboComment.id == comment_id).first()
            if comment:
                db.delete(comment)
                db.commit()
                return True
            return False