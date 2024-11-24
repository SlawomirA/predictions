from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from src.database import Base, engine_1

class File_Model(Base):
    __tablename__ = "File"

    FI_ID = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="Id liku")
    Name = Column(String(200), nullable=True, comment="Nazwa pliku")
    Content = Column(Text, nullable=True, comment="Zawartość tekstowa pliku")
    Corretted_Content = Column(Text, nullable=True, comment="Poprawiona przez program zawartość tekstu")
    Url = Column(String(300), nullable=True, comment="Url do pliku")

    messages = relationship("LLM_Message", back_populates="file")
    keywords = relationship("File_Keyword", back_populates="file")




Base.metadata.create_all(bind=engine)
