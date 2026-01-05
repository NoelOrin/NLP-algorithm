from typing import List, Dict, Any
from sqlalchemy.sql import func

from models.weibo_blog import WeiboBlog
from models.weibo_comment import WeiboComment
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
            
            # 将SQLAlchemy对象转换为字典，避免DetachedInstanceError
            blog_dict = {
                "id": blog.id,
                "bid": blog.bid,
                "user_id": blog.user_id,
                "screen_name": blog.screen_name,
                "text": blog.text,
                "created_time": blog.created_time
            }
            
            comments_list = []
            for comment in comments:
                comment_dict = {
                    "id": comment.id,
                    "bid": comment.bid,
                    "screen_name": comment.screen_name,
                    "text": comment.text,
                    "created_at": comment.created_at
                }
                comments_list.append(comment_dict)
            
            return {
                "blog": blog_dict,
                "comments": comments_list
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
                
                comment_dict = {
                    "id": comment.id,
                    "bid": comment.bid,
                    "screen_name": comment.screen_name,
                    "text": comment.text,
                    "created_at": comment.created_at
                }
                comments_by_blog[comment.bid].append(comment_dict)
            
            # 构建结果
            result = []
            for blog in blogs:
                blog_dict = {
                    "id": blog.id,
                    "bid": blog.bid,
                    "user_id": blog.user_id,
                    "screen_name": blog.screen_name,
                    "text": blog.text,
                    "created_time": blog.created_time
                }
                result.append({
                    "blog": blog_dict,
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
            # 第一步：随机获取指定数量的博客
            blogs = db.query(WeiboBlog).order_by(func.random()).limit(limit).all()
            
            if not blogs:
                return []
            
            # 获取这些博客的BID
            blog_bids = [blog.bid for blog in blogs]
            
            # 第二步：获取这些博客的所有评论
            comments = db.query(WeiboComment).filter(WeiboComment.bid.in_(blog_bids)).all()
            
            # 按博客BID分组评论
            comments_by_blog = {}
            for comment in comments:
                if comment.bid not in comments_by_blog:
                    comments_by_blog[comment.bid] = []
                
                comment_dict = {
                    "id": comment.id,
                    "bid": comment.bid,
                    "screen_name": comment.screen_name,
                    "text": comment.text,
                    "created_at": comment.created_at
                }
                comments_by_blog[comment.bid].append(comment_dict)
            
            # 构建最终结果
            result = []
            for blog in blogs:
                blog_dict = {
                    "id": blog.id,
                    "bid": blog.bid,
                    "user_id": blog.user_id,
                    "screen_name": blog.screen_name,
                    "text": blog.text,
                    "created_time": blog.created_time
                }
                
                result.append({
                    "blog": blog_dict,
                    "comments": comments_by_blog.get(blog.bid, [])
                })
            
        return result
    
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