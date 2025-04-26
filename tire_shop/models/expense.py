from app import db
from datetime import datetime
from enum import Enum

class ExpenseCategory(Enum):
    RENT = 'rent'
    UTILITIES = 'utilities'
    SALARIES = 'salaries'
    MAINTENANCE = 'maintenance'
    OTHER = 'other'

class PaymentMethod(Enum):
    CASH = 'cash'
    CHECK = 'check'
    CARD = 'card'
    TRANSFER = 'transfer'

class Expense(db.Model):
    __tablename__ = 'expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.Enum(ExpenseCategory), nullable=False)
    payment_method = db.Column(db.Enum(PaymentMethod), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    receipt_number = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    user = db.relationship('User')
    
    def __repr__(self):
        return f'<Expense {self.category.value} {self.amount}>'