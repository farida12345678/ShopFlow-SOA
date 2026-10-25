from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import engine, get_db, Base
from models import Product
from pydantic import BaseModel
from typing import List

# Création des tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ShopFlow REST API", version="1.0")

class ProductOut(BaseModel):
    id: int
    name: str
    description: str | None = None
    price: float
    stock: int
    is_active: bool

    class Config:
        from_attributes = True

@app.get("/")
def root():
    return {"message": "ShopFlow REST API is running"}

@app.get("/products", response_model=List[ProductOut])
def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).filter(Product.is_active == True).all()
    return products

@app.post("/products/seed")
def seed_products(db: Session = Depends(get_db)):
    """Ajoute des produits de test"""
    products = [
        Product(name="Laptop Pro 15", description="Ordinateur portable haute performance", price=1299.99, stock=12),
        Product(name="Souris sans fil", description="Souris ergonomique Bluetooth", price=29.90, stock=50),
        Product(name="Clavier mécanique", description="Clavier RGB switches bleus", price=89.00, stock=25),
        Product(name="Écran 27 pouces", description="Moniteur 4K IPS", price=349.50, stock=8),
        Product(name="Casque audio", description="Casque Bluetooth noise cancelling", price=159.00, stock=30),
    ]
    
    for p in products:
        db.add(p)
    db.commit()
    return {"message": f"{len(products)} produits ajoutés"}
