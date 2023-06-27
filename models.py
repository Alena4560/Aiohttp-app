import os
from atexit import register
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import (Column, DateTime, ForeignKey, Integer, String,
                        create_engine, func)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv('.env')
PG_USER = os.getenv('PG_USER')
PG_PASSWORD = os.getenv('PG_PASSWORD')
PG_DB = os.getenv('PG_DB')
PG_HOST = os.getenv('PG_HOST')
PG_PORT = os.getenv('PG_PORT')
PG_DSN = f'postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}'

engine = create_engine(PG_DSN)
register(engine.dispose)
Session = sessionmaker(engine)
Base = declarative_base()


class User(Base):
    __tablename__ = 'app_users'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True, index=True)
    email = Column(String(100), unique=True)
    password_hash = Column(String(128))
    creation_time = Column(DateTime, server_default=func.now())
    advertisements = relationship('Advertisement', backref='user', lazy='dynamic')

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Advertisement(Base):
    __tablename__ = 'app_advertisements'

    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    description = Column(String(500))
    owner = Column(String(50))
    creation_time = Column(DateTime, server_default=func.now())
    user_id = Column(Integer, ForeignKey('app_users.id'))

    def __init__(self, title, description, owner, user_id):
        self.title = title
        self.description = description
        self.owner = owner
        self.created_at = datetime.now()
        self.user_id = user_id


Base.metadata.create_all(engine)
