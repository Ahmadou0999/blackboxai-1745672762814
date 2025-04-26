from app import db
from datetime import datetime

class Tire(db.Model):
    __tablename__ = 'tires'
    
    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(80), nullable=False)
    model = db.Column(db.String(80), nullable=False)
    size = db.Column(db.String(20), nullable=False)
    width = db.Column(db.Integer, nullable=False)
    aspect_ratio = db.Column(db.Integer, nullable=False)
    diameter = db.Column(db.Integer, nullable=False)
    load_index = db.Column(db.String(10))
    speed_rating = db.Column(db.String(5))
    season = db.Column(db.String(20))  # summer, winter, all-season
    quantity = db.Column(db.Integer, default=0)
    purchase_price = db.Column(db.Float, nullable=False)
    selling_price = db.Column(db.Float, nullable=False)
    min_stock = db.Column(db.Integer, default=5)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    supplier = db.relationship('Supplier', back_populates='tires')
    transactions = db.relationship('Transaction', back_populates='tire')
    
    def __repr__(self):
        return f'<Tire {self.brand} {self.model} {self.size}>'