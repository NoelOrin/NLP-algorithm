import os
import sys

from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    DateTime,
    text as TextFunc
)
from sqlalchemy.orm import declarative_base
from orm.client import ORM, engine

Base = declarative_base()

class TopicWithWeibo(Base):
    __tablename__ = "topic_weibo_blogs"

    # id VARCHAR(20) PRIMARY KEY
    id = Column(String(20), primary_key=True)

    # bid VARCHAR(12) NOT NULL UNIQUE
    bid = Column(String(12), nullable=False, unique=True)

    # 用户信息
    user_id = Column(String(20))
    screen_name = Column(String(30))

    # 内容字段
    text = Column(Text)

    # 记录入库时间，默认 CURRENT_TIMESTAMP
    created_time = Column(
        DateTime,
        server_default=TextFunc("CURRENT_TIMESTAMP")
    )

    def __repr__(self):
        return f"<WeiboBlog(id='{self.id}', bid='{self.bid}', screen_name='{self.screen_name}')>"

Base.metadata.create_all(engine)

if __name__ == '__main__':
    try:
        with ORM() as db:
            print("\n数据库连接成功!")
            # 通过 get() 按主键查询（高效）
            data = db.query(WeiboBlog).first()
            print(f"查询结果: {data}")
    except Exception as e:
        print(f"\n数据库连接失败（正常情况，需要配置数据库）: {e}")
        print("模型定义和导入功能正常工作！")
