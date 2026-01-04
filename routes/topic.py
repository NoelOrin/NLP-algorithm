from fastapi import APIRouter
import os

router = APIRouter(prefix="/topic", tags=["data"])

@router.post("/classification")
async def topic_classification(request: TopicClassificationRequest):
    """主题提取"""
    return {
        "data": request
    }


@router.post("/similarity")
async def topic_similarity(request: TopicSimilarityRequest):
    """主题相似度"""
    return {
        "data": request
    }

@router.post("/classification")
async def topic_classification(request: TopicClassificationRequest):
    """主题热力图"""
    return {
        "data": request
    }


@router.post("/classification")
async def topic_classification(request: TopicClassificationRequest):
    """主题热力图"""
    return {
        "data": request
    }
