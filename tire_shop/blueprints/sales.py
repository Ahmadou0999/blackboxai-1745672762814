from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, abort
from flask_login import login_required, current_user
from wtforms import Form, IntegerField, FloatField, TextAreaField, SelectField, DateField, validators
from wtforms_sqlalchemy.fields import QuerySelectField
from ..models import Transaction, Tire, Supplier, TransactionType
from ..services.transaction_service import TransactionService
from ..services.tire_service import TireService
from .. import db
from datetime import datetime
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

sales_bp = Blueprint('sales', __name__, url_prefix='/sales')

class SalesForm(Form):
    transaction_type = SelectField('Transaction Type', choices=[(TransactionType.SALE.value, 'Sale')], default=TransactionType.SALE.value)
    tire = QuerySelectField('Tire', query_factory=lambda: Tire.query, get_label=lambda t: f"{t.brand} {t.model} {t.size}", validators=[validators.DataRequired()])
    quantity = IntegerField('Quantity', validators=[validators.DataRequired(), validators.NumberRange(min=1)])
    unit_price = FloatField('Unit Price', validators=[validators.DataRequired(), validators.NumberRange(min=0)])
    total_amount = FloatField('Total Amount', validators=[validators.DataRequired(), validators.NumberRange(min=0)])
    date = DateField('Date', default=datetime.utcnow, validators=[validators.DataRequired()])
    notes = TextAreaField('Notes')
    supplier = QuerySelectField('Supplier', query_factory=lambda: Supplier.query, get_label='name', validators=[validators.DataRequired()])

@sales_bp.route('/')
@login_required
def index():
    # Search/filter parameters
    tire_search = request.args.get('tire', '').strip()
    supplier_search = request.args.get('supplier', '').strip()
    date_from = request.args.get('date_from', '').strip()
    date_to = request.args.get('date_to', '').strip()

    query = Transaction.query.filter_by(transaction_type=TransactionType.SALE)

    if tire_search:
        query = query.join(Tire).filter(
            (Tire.brand.ilike(f'%{tire_search}%')) |
            (Tire.model.ilike(f'%{tire_search}%')) |
            (Tire.size.ilike(f'%{tire_search}%'))
        )
    if supplier_search:
        query = query.join(Supplier).filter(Supplier.name.ilike(f'%{supplier_search}%'))
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(Transaction.date >= date_from_obj)
        except ValueError:
            flash('Invalid start date format. Use YYYY-MM-DD.', 'warning')
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
            query = query.filter(Transaction.date <= date_to_obj)
        except ValueError:
            flash('Invalid end date format. Use YYYY-MM-DD.', 'warning')

    sales = query.order_by(Transaction.date.desc()).all()
    return render_template('sales/index.html', sales=sales, tire_search=tire_search, supplier_search=supplier_search, date_from=date_from, date_to=date_to)

@sales_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    form = SalesForm(request.form)
    if request.method == 'POST' and form.validate():
        tire = TireService.get_tire(form.tire.data.id)
        quantity = form.quantity.data
        if tire.quantity < quantity:
            flash(f'Insufficient stock for {tire.brand} {tire.model} {tire.size}. Available: {tire.quantity}', 'danger')
            return render_template('sales/form.html', form=form)
        data = {
            'transaction_type': TransactionType.SALE,
            'tire_id': tire.id,
            'quantity': quantity,
            'unit_price': form.unit_price.data,
            'total_amount': form.total_amount.data,
            'date': form.date.data,
            'notes': form.notes.data,
            'supplier_id': form.supplier.data.id,
            'user_id': current_user.id
        }
        try:
            TransactionService.create_transaction(data)
            # Decrement stock
            tire.quantity -= quantity
            db.session.commit()
            flash('Sale entry created successfully.', 'success')
            return redirect(url_for('sales.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating sale entry: {str(e)}', 'danger')
    return render_template('sales/form.html', form=form)

@sales_bp.route('/<int:sale_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(sale_id):
    sale = TransactionService.get_transaction(sale_id)
    if sale.transaction_type != TransactionType.SALE:
        flash('Invalid sale entry.', 'danger')
        return redirect(url_for('sales.index'))
    form = SalesForm(request.form, obj=sale)
    if request.method == 'POST' and form.validate():
        tire = TireService.get_tire(form.tire.data.id)
        new_quantity = form.quantity.data
        old_quantity = sale.quantity
        quantity_diff = new_quantity - old_quantity
        if quantity_diff > 0 and tire.quantity < quantity_diff:
            flash(f'Insufficient stock for {tire.brand} {tire.model} {tire.size}. Available: {tire.quantity}', 'danger')
            return render_template('sales/form.html', form=form, sale=sale)
        data = {
            'tire_id': tire.id,
            'quantity': new_quantity,
            'unit_price': form.unit_price.data,
            'total_amount': form.total_amount.data,
            'date': form.date.data,
            'notes': form.notes.data,
            'supplier_id': form.supplier.data.id,
            'user_id': current_user.id
        }
        try:
            TransactionService.update_transaction(sale_id, data)
            # Adjust stock
            tire.quantity -= quantity_diff
            db.session.commit()
            flash('Sale entry updated successfully.', 'success')
            return redirect(url_for('sales.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating sale entry: {str(e)}', 'danger')
    return render_template('sales/form.html', form=form, sale=sale)

@sales_bp.route('/<int:sale_id>')
@login_required
def view(sale_id):
    sale = TransactionService.get_transaction(sale_id)
    if sale.transaction_type != TransactionType.SALE:
        flash('Invalid sale entry.', 'danger')
        return redirect(url_for('sales.index'))
    return render_template('sales/view.html', sale=sale)

@sales_bp.route('/<int:sale_id>/delete', methods=['POST'])
@login_required
def delete(sale_id):
    try:
        TransactionService.delete_transaction(sale_id)
        flash('Sale entry deleted successfully.', 'success')
    except Exception as e:
        flash(f'Error deleting sale entry: {str(e)}', 'danger')
    return redirect(url_for('sales.index'))

@sales_bp.route('/<int:sale_id>/invoice')
@login_required
def invoice(sale_id):
    sale = TransactionService.get_transaction(sale_id)
    if sale.transaction_type != TransactionType.SALE:
        flash('Invalid sale entry.', 'danger')
        return redirect(url_for('sales.index'))

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Header
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, "Tire Shop Invoice")
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 70, f"Invoice ID: {sale.id}")
    p.drawString(50, height - 90, f"Date: {sale.date.strftime('%Y-%m-%d')}")

    # Customer/Supplier Info
    p.drawString(50, height - 130, f"Supplier: {sale.supplier.name if sale.supplier else 'N/A'}")

    # Sale Details
    p.drawString(50, height - 170, "Item:")
    p.drawString(150, height - 170, f"{sale.tire.brand} {sale.tire.model} {sale.tire.size}")
    p.drawString(50, height - 190, "Quantity:")
    p.drawString(150, height - 190, str(sale.quantity))
    p.drawString(50, height - 210, "Unit Price:")
    p.drawString(150, height - 210, f"${sale.unit_price:.2f}")
    p.drawString(50, height - 230, "Total Amount:")
    p.drawString(150, height - 230, f"${sale.total_amount:.2f}")

    # Footer
    p.drawString(50, height - 270, "Thank you for your business!")
    p.showPage()
    p.save()

    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"invoice_{sale.id}.pdf", mimetype='application/pdf')
