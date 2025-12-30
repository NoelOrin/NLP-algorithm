from fastapi import APIRouter
import os

router = APIRouter(prefix="/data", tags=["data"])


@router.get("/")
async def get_data_info():
    """获取数据信息"""
    # 获取数据目录下的文件信息
    data_dir = "e:\\项目\\NLP-algorithm\\data"
    files = []
    
    if os.path.exists(data_dir):
        for filename in os.listdir(data_dir):
            file_path = os.path.join(data_dir, filename)
            if os.path.isfile(file_path):
                file_size = os.path.getsize(file_path) / 1024 / 1024  # MB
                files.append({
                    "name": filename,
                    "size_mb": round(file_size, 2)
                })
    
    return {
        "message": "Data information",
        "data_count": len(files),
        "files": files
    }


@router.get("/types")
async def get_data_types():
    """获取数据类型"""
    return {
        "message": "Data types",
        "types": [
            "事件",
            "新闻", 
            "舆论",
            "合并数据"
        ]
    }