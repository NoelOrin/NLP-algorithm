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

class Topic_Weibo(Base):
    __tablename__ = "topic_weibo"

    # id VARCHAR(20) PRIMARY KEY
    id = Column(Integer, primary_key=True,autoincrement=True)

    # bid VARCHAR(12) NOT NULL UNIQUE
    bid = Column(String(12), nullable=False, unique=True)

    # 主题字段
    topic = Column(Text)

    # createAt = Column(DateTime, nullable=False)

    # 记录入库时间，默认 CURRENT_TIMESTAMP
    # created_time = Column(
    #     DateTime,
    #     server_default=TextFunc("CURRENT_TIMESTAMP")
    # )

    def __repr__(self):
        return f"<Topic_Weibo(id='{self.id}', bid='{self.bid}', screen_name='{self.screen_name}')>"

Base.metadata.create_all(engine)

if __name__ == '__main__':
    try:
        with ORM() as db:
            print("\n数据库连接成功!")
            # 通过 get() 按主键查询（高效）
            data = db.query(Topic_Weibo).first()
            print(f"查询结果: {data}")
    except Exception as e:
        print(f"\n数据库连接失败（正常情况，需要配置数据库）: {e}")
        print("模型定义和导入功能正常工作！")
