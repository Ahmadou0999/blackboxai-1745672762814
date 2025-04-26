from ..models import Transaction
from .. import db

class TransactionService:
    @staticmethod
    def get_all_transactions():
        return Transaction.query.all()

    @staticmethod
    def get_transaction(transaction_id):
        return Transaction.query.get_or_404(transaction_id)

    @staticmethod
    def create_transaction(data):
        transaction = Transaction(**data)
        db.session.add(transaction)
        db.session.commit()
        return transaction

    @staticmethod
    def update_transaction(transaction_id, data):
        transaction = Transaction.query.get_or_404(transaction_id)
        for key, value in data.items():
            setattr(transaction, key, value)
        db.session.commit()
        return transaction

    @staticmethod
    def delete_transaction(transaction_id):
        transaction = Transaction.query.get_or_404(transaction_id)
        db.session.delete(transaction)
        db.session.commit()
        return transaction