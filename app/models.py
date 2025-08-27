from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    api_key = Column(String(255), nullable=True)
    analyses = relationship("Analysis", back_populates="user")

class Analysis(Base):
    __tablename__ = "analyses"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    filename = Column(String(512), nullable=False)
    file_hash = Column(String(128), index=True, nullable=False, default="")
    result_json = Column(Text, nullable=True)
    status = Column(String(32), default="queued", index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="analyses")
