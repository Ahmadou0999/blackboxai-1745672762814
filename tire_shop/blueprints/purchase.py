from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from wtforms import Form, IntegerField, FloatField, TextAreaField, SelectField, DateField, validators
from wtforms_sqlalchemy.fields import QuerySelectField
from ..models import Transaction, Tire, Supplier, TransactionType
from ..services.transaction_service import TransactionService
from .. import db
from datetime import datetime

purchase_bp = Blueprint('purchase', __name__, url_prefix='/purchases')

class PurchaseForm(Form):
    transaction_type = SelectField('Transaction Type', choices=[(TransactionType.PURCHASE.value, 'Purchase')], default=TransactionType.PURCHASE.value)
    tire = QuerySelectField('Tire', query_factory=lambda: Tire.query, get_label=lambda t: f"{t.brand} {t.model} {t.size}", validators=[validators.DataRequired()])
    quantity = IntegerField('Quantity', validators=[validators.DataRequired(), validators.NumberRange(min=1)])
    unit_price = FloatField('Unit Price', validators=[validators.DataRequired(), validators.NumberRange(min=0)])
    total_amount = FloatField('Total Amount', validators=[validators.DataRequired(), validators.NumberRange(min=0)])
    date = DateField('Date', default=datetime.utcnow, validators=[validators.DataRequired()])
    notes = TextAreaField('Notes')
    supplier = QuerySelectField('Supplier', query_factory=lambda: Supplier.query, get_label='name', validators=[validators.DataRequired()])

@purchase_bp.route('/')
@login_required
def index():
    purchases = Transaction.query.filter_by(transaction_type=TransactionType.PURCHASE).order_by(Transaction.date.desc()).all()
    return render_template('purchase/index.html', purchases=purchases)

@purchase_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    form = PurchaseForm(request.form)
    if request.method == 'POST' and form.validate():
        data = {
            'transaction_type': TransactionType.PURCHASE,
            'tire_id': form.tire.data.id,
            'quantity': form.quantity.data,
            'unit_price': form.unit_price.data,
            'total_amount': form.total_amount.data,
            'date': form.date.data,
            'notes': form.notes.data,
            'supplier_id': form.supplier.data.id,
            'user_id': current_user.id
        }
        try:
            TransactionService.create_transaction(data)
            flash('Purchase entry created successfully.', 'success')
            return redirect(url_for('purchase.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating purchase entry: {str(e)}', 'danger')
    return render_template('purchase/form.html', form=form)

@purchase_bp.route('/<int:purchase_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(purchase_id):
    purchase = TransactionService.get_transaction(purchase_id)
    if purchase.transaction_type != TransactionType.PURCHASE:
        flash('Invalid purchase entry.', 'danger')
        return redirect(url_for('purchase.index'))
    form = PurchaseForm(request.form, obj=purchase)
    if request.method == 'POST' and form.validate():
        data = {
            'tire_id': form.tire.data.id,
            'quantity': form.quantity.data,
            'unit_price': form.unit_price.data,
            'total_amount': form.total_amount.data,
            'date': form.date.data,
            'notes': form.notes.data,
            'supplier_id': form.supplier.data.id,
            'user_id': current_user.id
        }
        try:
            TransactionService.update_transaction(purchase_id, data)
            flash('Purchase entry updated successfully.', 'success')
            return redirect(url_for('purchase.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating purchase entry: {str(e)}', 'danger')
    return render_template('purchase/form.html', form=form, purchase=purchase)

@purchase_bp.route('/<int:purchase_id>')
@login_required
def view(purchase_id):
    purchase = TransactionService.get_transaction(purchase_id)
    if purchase.transaction_type != TransactionType.PURCHASE:
        flash('Invalid purchase entry.', 'danger')
        return redirect(url_for('purchase.index'))
    return render_template('purchase/view.html', purchase=purchase)

@purchase_bp.route('/<int:purchase_id>/delete', methods=['POST'])
@login_required
def delete(purchase_id):
    try:
        TransactionService.delete_transaction(purchase_id)
        flash('Purchase entry deleted successfully.', 'success')
    except Exception as e:
        flash(f'Error deleting purchase entry: {str(e)}', 'danger')
    return redirect(url_for('purchase.index'))