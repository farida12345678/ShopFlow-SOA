from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine, get_db, Base
from models import Product, Order, OrderItem
from pydantic import BaseModel, EmailStr
from typing import List
from datetime import datetime

# Création des tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ShopFlow REST API", version="1.0")

# ========== SCHÉMAS ==========

class ProductOut(BaseModel):
    id: int
    name: str
    description: str | None = None
    price: float
    stock: int
    is_active: bool

    class Config:
        from_attributes = True

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    customer_name: str
    customer_email: str
    currency: str = "EUR"
    items: List[OrderItemCreate]

class OrderItemOut(BaseModel):
    product_id: int
    quantity: int
    unit_price: float

    class Config:
        from_attributes = True

class OrderOut(BaseModel):
    id: int
    customer_name: str
    customer_email: str
    currency: str
    total_eur: float
    total_converted: float | None
    status: str
    created_at: datetime
    items: List[OrderItemOut]

    class Config:
        from_attributes = True

# ========== ENDPOINTS ==========

@app.get("/")
def root():
    return {"message": "ShopFlow REST API is running"}

@app.get("/products", response_model=List[ProductOut])
def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).filter(Product.is_active == True).all()
    return products

@app.post("/products/seed")
def seed_products(db: Session = Depends(get_db)):
    """Ajoute des produits de test (à utiliser une seule fois)"""
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

@app.post("/orders", response_model=OrderOut)
def create_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    if not order_data.items:
        raise HTTPException(status_code=400, detail="La commande doit contenir au moins un produit")

    total_eur = 0.0
    order_items = []

    # Vérification du stock + calcul du total
    for item in order_data.items:
        product = db.query(Product).filter(Product.id == item.product_id, Product.is_active == True).first()
        
        if not product:
            raise HTTPException(status_code=404, detail=f"Produit {item.product_id} introuvable")
        
        if product.stock < item.quantity:
            raise HTTPException(
                status_code=400, 
                detail=f"Stock insuffisant pour {product.name}. Disponible : {product.stock}"
            )
        
        total_eur += product.price * item.quantity
        order_items.append({
            "product": product,
            "quantity": item.quantity,
            "unit_price": product.price
        })

    # Création de la commande
    new_order = Order(
        customer_name=order_data.customer_name,
        customer_email=order_data.customer_email,
        currency=order_data.currency.upper(),
        total_eur=round(total_eur, 2),
        total_converted=None,          # sera rempli plus tard avec l'API de change
        status="pending"
    )
    db.add(new_order)
    db.flush()  # pour obtenir l'ID de la commande

    # Création des lignes de commande + diminution du stock
    for item in order_items:
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=item["product"].id,
            quantity=item["quantity"],
            unit_price=item["unit_price"]
        )
        db.add(order_item)
        
        # Diminuer le stock
        item["product"].stock -= item["quantity"]

    db.commit()
    db.refresh(new_order)
    
    return new_order

@app.get("/orders/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Commande introuvable")
    return order