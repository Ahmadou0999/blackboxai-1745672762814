from app import db
from datetime import datetime
from enum import Enum

class TransactionType(Enum):
    PURCHASE = 'purchase'
    SALE = 'sale'

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_type = db.Column(db.Enum(TransactionType), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    tire_id = db.Column(db.Integer, db.ForeignKey('tires.id'))
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    tire = db.relationship('Tire', back_populates='transactions')
    supplier = db.relationship('Supplier', back_populates='transactions')
    user = db.relationship('User')
    
    def __repr__(self):
        return f'<Transaction {self.transaction_type.value} {self.quantity} tires>'