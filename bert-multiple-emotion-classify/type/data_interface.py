# 输入数据格式定义
from pydantic import BaseModel


class TextItem(BaseModel):
    text: str

class TextList(BaseModel):
    texts: list[str]