from typing import Annotated
from fastapi import Path
from urllib.request import Request
from typing import Optional

from fastapi import APIRouter
import os
from service.api.weibo.weibo_blog import weibo_blogs, weibo_blog
from service.api.weibo.weibo_comment import weibo_comment, weibo_comments

router = APIRouter(prefix="/data", tags=["data"])

@router.get("/blog/list")
async def get_blogs(
    page: int = 1,
    per_page: int = 20,
    screen_name: Optional[str] = None,
    order_by: Optional[str] = "created_time",
    order_desc: bool = True
):
    try:
        # 构建过滤条件
        filters = {}
        if screen_name:
            filters["screen_name"] = screen_name
            
        data = weibo_blogs(
            page=page,
            per_page=per_page,
            filters=filters,
            order_by=order_by,
            order_desc=order_desc
        )
        return {
            "data": data["items"],
            "pagination": data["pagination"]
        }
    except Exception as e:
        return {
            "error": str(e)
        }


@router.get("/blog/{id}")
async def get_blog(id: str):
    try:
        data = weibo_blog(id)
        return {
            "data": data
        }
    except Exception as e:
        return {
            "error": str(e)
        }

@router.get("/blog/{blog_id}/comments")
async def get_blog_comments(blog_id: Annotated[str, Path(description="微博博客ID")]):
    """获取指定博客的评论"""
    try:
        # 构建过滤条件
        filters = {"bid": blog_id}
        
        data = weibo_comments(
            page=1,
            per_page=100,  # 获取所有评论
            filters=filters,
            order_by="created_time",
            order_desc=True
        )
        return {
            "data": data["items"],
            "pagination": data["pagination"]
        }
    except Exception as e:
        return {
            "error": str(e)
        }

@router.get("/comments")
async def get_comments(
    page: int = 1,
    per_page: int = 20,
    blog_id: Optional[str] = None,
    order_by: Optional[str] = "created_time",
    order_desc: bool = True
):
    try:
        # 构建过滤条件
        filters = {}
        if blog_id:
            filters["bid"] = blog_id
            
        data = weibo_comments(
            page=page,
            per_page=per_page,
            filters=filters,
            order_by=order_by,
            order_desc=order_desc
        )
        return {
            "data": data["items"],
            "pagination": data["pagination"]
        }
    except Exception as e:
        return {
            "error": str(e)
        }

@router.get("/comment")
async def get_comment(id: str):
    try:
        data = weibo_comment(id)
        return {
            "data": data
        }
    except Exception as e:
        return {
            "error": str(e)
        }
