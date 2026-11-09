from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import engine, get_db
import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="StockLink API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    return {"message": "API StockLink funcionando"}

@app.get("/api/products")
def get_products(db: Session = Depends(get_db)):
    return db.query(models.Product).all()

@app.post("/api/products")
def create_product(prod: ProductSchema, db: Session = Depends(get_db)):
    nuevo = models.Product(**prod.dict())
    db.add(nuevo)
    db.commit()
    return {"message": "Producto guardado"}

@app.post("/api/sales")
def create_sale(sale: SaleSchema, db: Session = Depends(get_db)):
    nueva = models.Sale(total=sale.total, encargado=sale.encargado)
    db.add(nueva)
    db.commit()
    return {"message": "Venta registrada"}