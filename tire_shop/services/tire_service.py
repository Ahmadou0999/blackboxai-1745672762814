from ..models import Tire
from .. import db

class TireService:
    @staticmethod
    def get_all_tires():
        return Tire.query.all()

    @staticmethod
    def get_tire(tire_id):
        return Tire.query.get_or_404(tire_id)

    @staticmethod
    def create_tire(data):
        tire = Tire(**data)
        db.session.add(tire)
        db.session.commit()
        return tire

    @staticmethod
    def update_tire(tire_id, data):
        tire = Tire.query.get_or_404(tire_id)
        for key, value in data.items():
            setattr(tire, key, value)
        db.session.commit()
        return tire

    @staticmethod
    def delete_tire(tire_id):
        tire = Tire.query.get_or_404(tire_id)
        db.session.delete(tire)
        db.session.commit()
        return tire