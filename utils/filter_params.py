from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class FilterParams(BaseModel):
    """统一请求参数模型"""
    
    # 分页参数
    page: int = Field(default=1, ge=1, description="页码，从1开始")
    per_page: int = Field(default=20, ge=1, le=100, description="每页数量，最大100")
    
    # 排序参数
    order_by: Optional[str] = Field(default="created_time", description="排序字段")
    order_desc: bool = Field(default=True, description="是否降序排列")
    
    # 通用过滤参数
    filters: Optional[Dict[str, Any]] = Field(default=None, description="过滤条件字典")
    
    # 特定实体过滤参数
    screen_name: Optional[str] = Field(default=None, description="用户名过滤（用于博客）")
    blog_id: Optional[str] = Field(default=None, description="博客ID过滤（用于评论）")
    
    class Config:
        """Pydantic配置"""
        schema_extra = {
            "example": {
                "page": 1,
                "per_page": 20,
                "order_by": "created_time",
                "order_desc": True,
                "screen_name": "example_user",
                "blog_id": "1234567890"
            }
        }


def build_filters_from_params(params: FilterParams) -> Dict[str, Any]:
    """
    从FilterParams构建过滤条件字典
    
    Args:
        params: FilterParams实例
        
    Returns:
        过滤条件字典
    """
    filters = {}
    
    # 添加特定过滤条件
    if params.screen_name:
        filters["screen_name"] = params.screen_name
    
    if params.blog_id:
        filters["bid"] = params.blog_id  # 评论表中使用bid字段
    
    # 合并自定义过滤条件
    if params.filters:
        filters.update(params.filters)
    
    return filters