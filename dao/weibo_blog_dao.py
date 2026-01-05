from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Query

from data_models.weibo_blog import WeiboBlog
from orm.client import ORM


class WeiboBlogDAO:
    """微博博客数据访问对象"""
    
    @staticmethod
    def get_by_id(blog_id: str) -> Optional[WeiboBlog]:
        """根据ID获取微博博客"""
        with ORM() as db:
            return db.query(WeiboBlog).filter(WeiboBlog.id == blog_id).first()
    
    @staticmethod
    def get_by_ids(blog_ids: List[str]) -> List[WeiboBlog]:
        """根据ID列表获取微博博客列表"""
        with ORM() as db:
            return db.query(WeiboBlog).filter(WeiboBlog.id.in_(blog_ids)).all()
    
    @staticmethod
    def get_by_bid(blog_bid: str) -> Optional[WeiboBlog]:
        """根据BID获取微博博客"""
        with ORM() as db:
            return db.query(WeiboBlog).filter(WeiboBlog.bid == blog_bid).first()
    
    @staticmethod
    def get_by_bids(blog_bids: List[str]) -> List[WeiboBlog]:
        """根据BID列表获取微博博客列表"""
        with ORM() as db:
            return db.query(WeiboBlog).filter(WeiboBlog.bid.in_(blog_bids)).all()
    
    @staticmethod
    def get_by_screen_name(screen_name: str) -> List[WeiboBlog]:
        """根据用户名获取微博博客列表"""
        with ORM() as db:
            return db.query(WeiboBlog).filter(WeiboBlog.screen_name == screen_name).all()
    
    @staticmethod
    def get_all() -> List[WeiboBlog]:
        """获取所有微博博客"""
        with ORM() as db:
            return db.query(WeiboBlog).all()
    
    @staticmethod
    def count() -> int:
        """获取微博博客总数"""
        with ORM() as db:
            return db.query(WeiboBlog).count()
    
    @staticmethod
    def get_paginated(
        page: int = 1,
        per_page: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        order_desc: bool = False
    ) -> Dict[str, Any]:
        """
        获取分页的微博博客列表
        
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
            query: Query = db.query(WeiboBlog)
            
            # 应用过滤条件
            if filters:
                for field, value in filters.items():
                    if hasattr(WeiboBlog, field):
                        query = query.filter(getattr(WeiboBlog, field) == value)
            
            # 计算总数
            total_count = query.count()
            total_pages = (total_count + per_page - 1) // per_page
            
            # 应用排序
            if order_by and hasattr(WeiboBlog, order_by):
                order_field = getattr(WeiboBlog, order_by)
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
    def create(blog_data: Dict[str, Any]) -> WeiboBlog:
        """创建微博博客"""
        with ORM() as db:
            blog = WeiboBlog(**blog_data)
            db.add(blog)
            db.commit()
            db.refresh(blog)
            return blog
    
    @staticmethod
    def update(blog_id: str, update_data: Dict[str, Any]) -> Optional[WeiboBlog]:
        """更新微博博客"""
        with ORM() as db:
            blog = db.query(WeiboBlog).filter(WeiboBlog.id == blog_id).first()
            if blog:
                for key, value in update_data.items():
                    if hasattr(blog, key):
                        setattr(blog, key, value)
                db.commit()
                db.refresh(blog)
            return blog
    
    @staticmethod
    def delete(blog_id: str) -> bool:
        """删除微博博客"""
        with ORM() as db:
            blog = db.query(WeiboBlog).filter(WeiboBlog.id == blog_id).first()
            if blog:
                db.delete(blog)
                db.commit()
                return True
            return False