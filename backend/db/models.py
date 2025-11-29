from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Vehicle(Base):
    __tablename__ = "vehicles"
    id = Column(Integer, primary_key=True, index=True)
    number = Column(String, index=True)
    owner = Column(String, index=True)
    image_path = Column(String)
    timestamp = Column(String)
