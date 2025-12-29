from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class AuthActivityLog(Base):
    __tablename__ = "auth_activity_logs"

    id = Column(Integer, primary_key=True)
    user_email = Column(String(255))
    user_role = Column(String(50))
    ip_address = Column(String(45))
    auth_method = Column(String(50))
    status = Column(String(20))
    user_agent = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

class SystemEvent(Base):
    __tablename__ = "system_events"

    id = Column(Integer, primary_key=True)
    event_type = Column(String(50))
    severity = Column(String(20))
    message = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
