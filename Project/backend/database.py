from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from datetime import datetime


# Configuración de la base de datos
DATABASE_URL = "sqlite:///./test.db"  # Cambia esto por tu conexión de base de datos real

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Modelo de usuario
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

# Modelo de enlaces
class Link(Base):
    __tablename__ = 'links'

    id = Column(Integer, primary_key=True)
    url = Column(String)
    descripcion = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    contenido = Column(String)  # Verifica que esta línea esté presente
    titulo = Column(String)
    categoria = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)  # Establece la fecha de creación
    

# Crear las tablas en la base de datos
def init_db():
    Base.metadata.create_all(bind=engine)

# Inicializa la base de datos (esto solo debe hacerse una vez)
if __name__ == "__main__":
    init_db()