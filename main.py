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

# --- SEGURIDAD ---
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

# --- MODELOS ---
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

# --- RUTAS ---
@app.get("/")
def home():
    return {"message": "API StockLink Segura"}

@app.post("/api/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.password == "123":
        rol = "dueno" if "dueno" in form_data.username else "encargado"
        token = crear_token({"sub": form_data.username, "rol": rol})
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Contraseña incorrecta (usa 123)")

# --- RUTAS PROTEGIDAS (Requieren Token) ---
@app.get("/api/products")
def get_products(db: Session = Depends(get_db), user: dict = Depends(verificar_token)):
    return db.query(models.Product).all()

@app.post("/api/products")
def create_product(prod: ProductSchema, db: Session = Depends(get_db), user: dict = Depends(verificar_token)):
    nuevo = models.Product(**prod.dict())
    db.add(nuevo)
    db.commit()
    return {"message": "Producto guardado"}

@app.post("/api/sales")
def create_sale(sale: SaleSchema, db: Session = Depends(get_db), user: dict = Depends(verificar_token)):
    nueva = models.Sale(total=sale.total, encargado=sale.encargado)
    db.add(nueva)
    db.commit()
    return {"message": "Venta registrada"}

@app.get("/api/sales")
def get_sales(db: Session = Depends(get_db), user: dict = Depends(verificar_token)):
    return db.query(models.Sale).order_by(models.Sale.time.desc()).all()