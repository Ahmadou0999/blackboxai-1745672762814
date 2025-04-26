from ..models import Expense
from .. import db

class ExpenseService:
    @staticmethod
    def get_all_expenses():
        return Expense.query.all()

    @staticmethod
    def get_expense(expense_id):
        return Expense.query.get_or_404(expense_id)

    @staticmethod
    def create_expense(data):
        expense = Expense(**data)
        db.session.add(expense)
        db.session.commit()
        return expense

    @staticmethod
    def update_expense(expense_id, data):
        expense = Expense.query.get_or_404(expense_id)
        for key, value in data.items():
            setattr(expense, key, value)
        db.session.commit()
        return expense

    @staticmethod
    def delete_expense(expense_id):
        expense = Expense.query.get_or_404(expense_id)
        db.session.delete(expense)
        db.session.commit()
        return expense