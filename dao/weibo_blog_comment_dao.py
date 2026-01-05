from typing import List, Dict, Any
from sqlalchemy.sql import func

from data_models.weibo_blog import WeiboBlog
from data_models.weibo_comment import WeiboComment
from orm.client import ORM


class WeiboBlogCommentDAO:
    """微博博客和评论联合数据访问对象"""
    
    @staticmethod
    def get_blog_with_comments(blog_id: str) -> Dict[str, Any]:
        """
        根据博客ID获取博客及其评论
        
        Args:
            blog_id: 博客ID
            
        Returns:
            包含博客和评论的字典
        """
        with ORM() as db:
            # 获取博客
            blog = db.query(WeiboBlog).filter(WeiboBlog.id == blog_id).first()
            if not blog:
                return None
            
            # 获取评论
            comments = db.query(WeiboComment).filter(WeiboComment.bid == blog.bid).all()
            
            return {
                "blog": blog,
                "comments": comments
            }
    
    @staticmethod
    def get_blogs_with_comments(blog_ids: List[str]) -> List[Dict[str, Any]]:
        """
        根据博客ID列表获取博客及其评论列表
        
        Args:
            blog_ids: 博客ID列表
            
        Returns:
            包含博客和评论的字典列表
        """
        with ORM() as db:
            # 获取博客列表
            blogs = db.query(WeiboBlog).filter(WeiboBlog.id.in_(blog_ids)).all()
            if not blogs:
                return []
            
            # 获取所有相关评论
            blog_bids = [blog.bid for blog in blogs]
            comments = db.query(WeiboComment).filter(WeiboComment.bid.in_(blog_bids)).all()
            
            # 按博客分组评论
            comments_by_blog = {}
            for comment in comments:
                if comment.bid not in comments_by_blog:
                    comments_by_blog[comment.bid] = []
                comments_by_blog[comment.bid].append(comment)
            
            # 构建结果
            result = []
            for blog in blogs:
                result.append({
                    "blog": blog,
                    "comments": comments_by_blog.get(blog.bid, [])
                })
            
            return result
    
    @staticmethod
    def get_random_blogs_with_comments(limit: int = 10) -> List[Dict[str, Any]]:
        """
        随机获取博客及其评论
        
        Args:
            limit: 获取数量
            
        Returns:
            包含博客和评论的字典列表
        """
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
                        "blog": blog,
                        "comments": []
                    }
                if comment:
                    result_map[blog.bid]["comments"].append(comment)
            
            return list(result_map.values())
    
    @staticmethod
    def get_comments_by_blog_id(blog_id: str) -> List[WeiboComment]:
        """根据博客ID获取评论列表"""
        with ORM() as db:
            return db.query(WeiboComment).filter(WeiboComment.bid == blog_id).all()
    
    @staticmethod
    def get_comments_by_blog_ids(blog_ids: List[str]) -> List[WeiboComment]:
        """根据博客ID列表获取评论列表"""
        with ORM() as db:
            return db.query(WeiboComment).filter(WeiboComment.bid.in_(blog_ids)).all()
    
    @staticmethod
    def get_comment_counts_by_blog_ids(blog_ids: List[str]) -> Dict[str, int]:
        """
        根据博客ID列表获取每个博客的评论数量
        
        Args:
            blog_ids: 博客ID列表
            
        Returns:
            博客ID到评论数量的映射字典
        """
        with ORM() as db:
            # 获取博客对应的BID
            blogs = db.query(WeiboBlog).filter(WeiboBlog.id.in_(blog_ids)).all()
            blog_bids = [blog.bid for blog in blogs]
            
            # 统计每个BID的评论数量
            from sqlalchemy import func
            result = db.query(
                WeiboComment.bid,
                func.count(WeiboComment.id).label('comment_count')
            ).filter(WeiboComment.bid.in_(blog_bids)).group_by(WeiboComment.bid).all()
            
            # 构建结果映射
            comment_counts = {}
            for bid, count in result:
                comment_counts[bid] = count
            
            # 将BID映射回ID
            blog_id_to_bid = {blog.bid: blog.id for blog in blogs}
            return {blog_id_to_bid.get(bid, bid): count for bid, count in comment_counts.items()}