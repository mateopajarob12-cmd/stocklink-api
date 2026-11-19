from typing import List
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

def solo_propietario(user: dict = Depends(verificar_token)):
    if user.get("rol") != "propietario":
        raise HTTPException(status_code=403, detail="Solo el administrador puede hacer esto")
    return user

class ProductSchema(BaseModel):
    code: str
    name: str
    category: str
    stock: int
    minStock: int
    price: float

class SaleItemSchema(BaseModel):
    code: str
    quantity: int

class SaleCreateSchema(BaseModel):
    items: List[SaleItemSchema]

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
def create_sale(sale: SaleCreateSchema, db: Session = Depends(get_db), user: dict = Depends(verificar_token)):
    if not sale.items:
        raise HTTPException(status_code=400, detail="La venta está vacía")

    # Juntar cantidades si un código viene repetido
    cantidades = {}
    for it in sale.items:
        if it.quantity <= 0:
            raise HTTPException(status_code=400, detail="Cantidad inválida")
        cantidades[it.code] = cantidades.get(it.code, 0) + it.quantity

    # Validar TODO el stock antes de tocar nada
    lineas = []
    total = 0.0
    for code, qty in cantidades.items():
        prod = db.query(models.Product).filter(models.Product.code == code).with_for_update().first()
        if not prod:
            raise HTTPException(status_code=404, detail=f"El producto {code} no existe")
        if prod.stock < qty:
            raise HTTPException(status_code=400, detail=f"Stock insuficiente: {prod.name}")
        lineas.append((prod, qty))
        total += prod.price * qty

    nueva = models.Sale(total=total, encargado=user["sub"])
    db.add(nueva)
    db.flush()
    for prod, qty in lineas:
        prod.stock -= qty
        db.add(models.SaleItem(sale_id=nueva.id, product_id=prod.id, quantity=qty, unit_price=prod.price))
    db.commit()
    return {"message": "Venta registrada", "id": nueva.id, "total": total}

@app.get("/api/sales")
def get_sales(db: Session = Depends(get_db), user: dict = Depends(solo_propietario)):
    return db.query(models.Sale).order_by(models.Sale.time.desc()).all()