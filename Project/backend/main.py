from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from passlib.context import CryptContext
from database import User, Link, init_db, SessionLocal  # Asegúrate de que estos importen correctamente
from sqlalchemy.exc import IntegrityError
import requests
from bs4 import BeautifulSoup
import joblib
from sklearn.pipeline import make_pipeline
from fastapi.responses import JSONResponse
import os
from typing import List, Optional
from uuid import UUID
from datetime import datetime
import uvicorn

# Inicializa FastAPI
app = FastAPI()

# Inicializa la base de datos
init_db()

# Configuración de seguridad
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Modelo para la descripción
class LinkUpdate(BaseModel):
    descripcion: str
    updated_at: str 

# Modelo Pydantic para el usuario
class UserCreate(BaseModel):
    username: str
    password: str

class UserInDB(UserCreate):
    hashed_password: str

class LinkCreate(BaseModel):
    url: str
    descripcion: str

model_path = 'C:/Users/DELL/Documents/proyecto_desarrollo/modelo/model_Category/model_category.pk'
model1 = joblib.load(model_path)

def predecir_categoria(contenido):
    # Asumiendo que el modelo espera una lista o array
    categoria_predicha = model1.predict([contenido])[0]  # Devuelve la primera predicción
    return categoria_predicha

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def extraer_informacion(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extrae el título
        titulo = soup.title.string if soup.title else 'Sin título'

        # Extrae los párrafos y toma las primeras 40 palabras
        parrafos = soup.find_all('p')
        contenido = ' '.join([p.get_text() for p in parrafos])
        contenido_resumido = ' '.join(contenido.split()[:40])  # Toma solo las primeras 20 palabras

        return titulo, contenido_resumido

    except Exception as e:
        return None, None

@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(username=user.username, password=hashed_password)

    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Username already registered")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    return {"msg": "User registered successfully!"}

# Función para autenticar al usuario
@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not pwd_context.verify(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return {"access_token": user.username, "token_type": "bearer"}

# Endpoint para verificar el estado del usuario autenticado
@app.get("/users/me")
def read_users_me(token: str = Depends(oauth2_scheme)):
    return {"token": token}  # Aquí podrías devolver información del usuario

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()  # Obtiene todos los usuarios
    return users

@app.post("/links")
def create_link(link: LinkCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    # Obtén el usuario correspondiente al token
    user = db.query(User).filter(User.username == token).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Extraer título y contenido del enlace
    titulo, contenido = extraer_informacion(link.url)

    if not titulo:
        raise HTTPException(status_code=400, detail="Could not extract information from the URL")

    # Predecir la categoría con el modelo de ML
    categoria = predecir_categoria(contenido)

    new_link = Link(url=link.url, descripcion=link.descripcion, user_id=user.id, titulo=titulo, contenido=contenido, categoria=categoria)
    db.add(new_link)
    db.commit()
    db.refresh(new_link)
    return new_link


@app.get("/links")
def get_links(search: Optional[str] = None, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user = db.query(User).filter(User.username == token).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    query = db.query(Link).filter(Link.user_id == user.id)

    if search:
        # Filtrar enlaces por descripción o título
        query = query.filter((Link.descripcion.ilike(f"%{search}%")) | (Link.titulo.ilike(f"%{search}%")))

    links = query.all()
    return links

@app.delete("/links/{link_id}")
def delete_link(link_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    # Obtener el usuario correspondiente al token
    user = db.query(User).filter(User.username == token).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Buscar el enlace por ID y verificar que pertenece al usuario
    link = db.query(Link).filter(Link.id == link_id, Link.user_id == user.id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    # Eliminar el enlace de la base de datos
    db.delete(link)
    db.commit()
    
    return {"msg": "Link deleted successfully"}

@app.get("/links/")
def read_links(db: Session = Depends(get_db)):
    links = get_links(db)
    return links

@app.get("/links")
def get_links(
    search: str = None, 
    categoria: str = None, 
    db: Session = Depends(get_db), 
    token: str = Depends(oauth2_scheme)
):
    user = db.query(User).filter(User.username == token).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    query = db.query(Link).filter(Link.user_id == user.id)

    if search:
        # Filtrar enlaces por descripción o título
        query = query.filter((Link.descripcion.ilike(f"%{search}%")) | (Link.titulo.ilike(f"%{search}%")))

    if categoria:
        # Filtrar enlaces por categoría
        query = query.filter(Link.categoria == categoria)

    links = query.all()
    return links

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
