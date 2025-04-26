from app import db

class Supplier(db.Model):
    __tablename__ = 'suppliers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    contact_person = db.Column(db.String(80))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    address = db.Column(db.Text)
    tax_id = db.Column(db.String(50))
    payment_terms = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    
    tires = db.relationship('Tire', back_populates='supplier')
    transactions = db.relationship('Transaction', back_populates='supplier')
    
    def __repr__(self):
        return f'<Supplier {self.name}>'