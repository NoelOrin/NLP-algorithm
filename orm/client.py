import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from sqlalchemy.orm import Session
from typing import Iterator, ContextManager

# 数据库 URL（PostgreSQL）
DATABASE_URL = "postgresql://noel_orin:Aa18520863834@localhost:5432/nlp_db"  # 同步

engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@contextmanager
def ORM() -> ContextManager[Session]:
    db = SessionLocal()  # 创建会话
    try:
        yield db  # 提供会话给外部使用
        db.commit()  # 无异常时提交事务
        # print("事务提交成功")
    except Exception as e:
        db.rollback()  # 异常时回滚事务
        print(f"事务回滚：{str(e)}")
        raise  # 抛出异常供外部处理
    finally:
        db.close()  # 无论成败都关闭会话
        # print("会话已关闭")
