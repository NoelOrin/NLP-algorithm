from fastapi import APIRouter

router = APIRouter(prefix="", tags=["index"])


@router.get("/")
async def get_index():
    """首页"""
    return {
        "message": "Welcome to NLP Algorithm API",
        "version": "1.0.0",
        "endpoints": {
            "index": "/",
            "data": "/data"
        }
    }