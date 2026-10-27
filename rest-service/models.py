from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)          # Prix en EUR
    stock = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    # Relation avec les commandes
    order_items = relationship("OrderItem", back_populates="product")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    customer_email = Column(String, nullable=False)
    currency = Column(String, default="EUR")       # Devise choisie par le client
    total_eur = Column(Float, nullable=False)      # Montant total en EUR
    total_converted = Column(Float, nullable=True) # Montant converti
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)     # Prix unitaire au moment de la commande

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")