from typing import List, Dict, Any

from dao.weibo_blog_comment_dao import WeiboBlogCommentDAO


def weibo_blog_comments(blog_id: str) -> Dict[str, Any]:
    """根据博客ID获取博客及其评论"""
    result = WeiboBlogCommentDAO.get_blog_with_comments(blog_id)
    return {
        "data": result
    }


def weibo_blogs_comments(blog_ids: List[str]) -> Dict[str, Any]:
    """根据博客ID列表获取博客及其评论列表"""
    results = WeiboBlogCommentDAO.get_blogs_with_comments(blog_ids)
    return {
        "data": results
    }


def weibo_blog_random(limit: int = 10) -> Dict[str, Any]:
    """随机获取微博+评论"""
    results = WeiboBlogCommentDAO.get_random_blogs_with_comments(limit)
    return {
        "data": results
    }


if __name__ == '__main__':
    print(weibo_blog_random(10))
