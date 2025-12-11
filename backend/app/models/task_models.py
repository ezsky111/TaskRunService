from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    description = Column(Text)
    scripts = relationship('Script', order_by='Script.order', back_populates='task')
    runs = relationship('TaskRun', back_populates='task')

class Script(Base):
    __tablename__ = 'scripts'
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    filename = Column(String(128), nullable=False)
    order = Column(Integer, nullable=False)
    task = relationship('Task', back_populates='scripts')

class TaskRun(Base):
    __tablename__ = 'task_runs'
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    finished_at = Column(DateTime)
    status = Column(String(32))
    initial_context = Column(JSON)  # 初始环境变量
    final_context = Column(JSON)    # 最终环境变量
    logs = relationship('TaskRunLog', back_populates='run')
    contexts = relationship('TaskRunContext', back_populates='run')
    task = relationship('Task', back_populates='runs')

class TaskRunLog(Base):
    __tablename__ = 'task_run_logs'
    id = Column(Integer, primary_key=True)
    run_id = Column(Integer, ForeignKey('task_runs.id'))
    script_filename = Column(String(128))
    output = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    run = relationship('TaskRun', back_populates='logs')

class TaskRunContext(Base):
    """记录每个脚本执行后生成的环境变量"""
    __tablename__ = 'task_run_contexts'
    id = Column(Integer, primary_key=True)
    run_id = Column(Integer, ForeignKey('task_runs.id'))
    script_filename = Column(String(128))
    context = Column(JSON)  # 该脚本执行后生成的环境变量
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    run = relationship('TaskRun', back_populates='contexts')


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    roles = Column(String(256), default='user')
