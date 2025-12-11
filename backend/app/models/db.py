from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .task_models import Base
import os
from werkzeug.security import generate_password_hash
from .task_models import User
from sqlalchemy.exc import SQLAlchemyError

DB_PATH = os.getenv('TASK_DB_PATH', f"sqlite:///{os.path.abspath(os.path.join(os.path.dirname(__file__), '../../db/taskrun.db'))}")
engine = create_engine(DB_PATH, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    # 创建表
    Base.metadata.create_all(bind=engine)

    # 在创建表后，检查 users 表或初始用户是否存在；若不存在，则插入初始管理员
    session = SessionLocal()
    try:
        init_user = os.getenv('INIT_ADMIN_USER', 'admin')
        init_password = os.getenv('INIT_ADMIN_PASSWORD') or os.getenv('DEMO_USER_PASSWORD') or 'password'

        try:
            # 优先查找指定的初始用户
            existing_init = session.query(User).filter_by(username=init_user).first()
        except Exception:
            existing_init = None

        if not existing_init:
            try:
                any_user = session.query(User).first()
            except Exception:
                any_user = None

            # 如果用户表为空或指定初始用户不存在，则插入初始管理员
            if any_user is None or existing_init is None:
                pwd_hash = generate_password_hash(init_password)
                user = User(username=init_user, password_hash=pwd_hash, roles='admin')
                session.add(user)
                session.commit()
    except SQLAlchemyError:
        session.rollback()
    finally:
        session.close()
