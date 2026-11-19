from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from jose import JWTError, jwt
from datetime import datetime, timedelta
from database import engine, get_db
import models

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = "stocklink_2026_secreto"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")

def crear_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=2)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verificar_token(token: str = Depends(oauth2_scheme)):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

class ProductSchema(BaseModel):
    code: str
    name: str
    category: str
    stock: int
    minStock: int
    price: float

class SaleSchema(BaseModel):
    total: float
    encargado: str

@app.get("/")
def home():
    return {"message": "API StockLink Segura"}

@app.post("/api/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.password != "123":
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")
    
    if form_data.username == "propietario@stocklink.com":
        rol = "propietario"
    elif form_data.username == "encargado@stocklink.com":
        rol = "encargado"
    else:
        raise HTTPException(status_code=401, detail="Correo no registrado en el sistema")
        
    token = crear_token({"sub": form_data.username, "rol": rol})
    
    # ¡AQUÍ ESTÁ LA LÍNEA QUE FALTA! Enviar el rol a Flutter
    return {"access_token": token, "token_type": "bearer", "rol": rol}
    
@app.get("/api/products")
def get_products(db: Session = Depends(get_db), user: dict = Depends(verificar_token)):
    return db.query(models.Product).all()

@app.post("/api/products")
def create_product(prod: ProductSchema, db: Session = Depends(get_db), user: dict = Depends(verificar_token)):
    if db.query(models.Product).filter(models.Product.code == prod.code).first():
        raise HTTPException(status_code=400, detail="Ya existe un producto con ese código")
    nuevo = models.Product(**prod.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return {"message": "Producto guardado", "id": nuevo.id}

@app.post("/api/sales")
def create_sale(sale: SaleSchema, db: Session = Depends(get_db), user: dict = Depends(verificar_token)):
    nueva = models.Sale(total=sale.total, encargado=sale.encargado)
    db.add(nueva)
    db.commit()
    return {"message": "Venta registrada"}

@app.get("/api/sales")
def get_sales(db: Session = Depends(get_db), user: dict = Depends(verificar_token)):
    return db.query(models.Sale).order_by(models.Sale.time.desc()).all()