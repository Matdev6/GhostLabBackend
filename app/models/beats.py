from sqlalchemy import Column, Integer, String, Boolean
from app.db.database import Base

class Beats(Base):
    __tablename__ = "beats"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    audio_path = Column(String)
    image_path = Column(String)
    exclusive = Column(Boolean)
