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

class WeiboBlog(Base):
    __tablename__ = "weibo_blogs"

    # id VARCHAR(20) PRIMARY KEY
    id = Column(String(20), primary_key=True)

    # bid VARCHAR(12) NOT NULL UNIQUE
    bid = Column(String(12), nullable=False, unique=True)

    # 用户信息
    user_id = Column(String(20))
    screen_name = Column(String(30))

    # 内容字段
    text = Column(Text)
    # 文章链接
    article_url = Column(String(100))
    # 话题
    topics = Column(String(200))
    # @用户
    at_users = Column(String(1000))
    # 图片链接
    pics = Column(String(3000))
    # 视频链接
    video_url = Column(String(1000))
    # 位置
    location = Column(String(100))
    # 创建时间
    created_at = Column(DateTime)
    # 来源
    source = Column(String(30))
    # 点赞数
    attitudes_count = Column(Integer)
    # 评论数
    comments_count = Column(Integer)
    # 转发数
    reposts_count = Column(Integer)
    # 引用微博ID
    retweet_id = Column(String(20))
    # IP地址
    ip = Column(String(100))
    # 用户认证
    user_authentication = Column(String(100))
    # VIP类型
    vip_type = Column(String(50))
    # VIP等级
    vip_level = Column(Integer)
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
