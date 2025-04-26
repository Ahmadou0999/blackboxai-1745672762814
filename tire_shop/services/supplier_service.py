from ..models import Supplier
from .. import db

class SupplierService:
    @staticmethod
    def get_all_suppliers():
        return Supplier.query.all()

    @staticmethod
    def get_supplier(supplier_id):
        return Supplier.query.get_or_404(supplier_id)

    @staticmethod
    def create_supplier(data):
        supplier = Supplier(**data)
        db.session.add(supplier)
        db.session.commit()
        return supplier

    @staticmethod
    def update_supplier(supplier_id, data):
        supplier = Supplier.query.get_or_404(supplier_id)
        for key, value in data.items():
            setattr(supplier, key, value)
        db.session.commit()
        return supplier

    @staticmethod
    def delete_supplier(supplier_id):
        supplier = Supplier.query.get_or_404(supplier_id)
        db.session.delete(supplier)
        db.session.commit()
        return supplier