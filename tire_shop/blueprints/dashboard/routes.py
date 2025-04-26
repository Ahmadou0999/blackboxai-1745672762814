from flask import render_template, request, jsonify, flash, redirect, url_for, Response
from flask_login import login_required, current_user
from ..models import Tire, Supplier, Transaction, Expense, UserActivityLog
from .. import db
from datetime import datetime, timedelta
from .forms import TireForm, TransactionForm, ExpenseForm
from sqlalchemy import func, or_
from sqlalchemy.exc import SQLAlchemyError
import csv
import io

@dashboard_bp.route('/')
@login_required
def index():
    # Dashboard statistics
    total_tires = Tire.query.count()
    low_stock = Tire.query.filter(Tire.quantity < Tire.min_stock).count()
    total_sales = db.session.query(
        func.sum(Transaction.total_amount)
    ).filter(
        Transaction.transaction_type == 'sale'
    ).scalar() or 0
    
    # Weekly sales data
    weekly_sales = db.session.query(
        func.date(Transaction.date),
        func.sum(Transaction.total_amount)
    ).filter(
        Transaction.transaction_type == 'sale',
        Transaction.date >= datetime.now() - timedelta(days=7)
    ).group_by(
        func.date(Transaction.date)
    ).all()

    # Notifications for low stock
    notifications = []
    if low_stock > 0:
        notifications.append(f"There are {low_stock} items low in stock.")

    # Recent user activity logs
    recent_logs = UserActivityLog.query.order_by(UserActivityLog.timestamp.desc()).limit(5).all()
    
    return render_template('dashboard/index.html',
                         total_tires=total_tires,
                         low_stock=low_stock,
                         total_sales=total_sales,
                         weekly_sales=weekly_sales,
                         notifications=notifications,
                         recent_logs=recent_logs)

@dashboard_bp.route('/export/transactions')
@login_required
def export_transactions():
    if not current_user.is_admin:
        return "Unauthorized", 403
    transactions = Transaction.query.order_by(Transaction.date.desc()).all()
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['Date', 'Type', 'Tire', 'Quantity', 'Unit Price', 'Total', 'Supplier', 'Notes'])
    for t in transactions:
        cw.writerow([
            t.date.strftime('%Y-%m-%d'),
            t.transaction_type,
            f"{t.tire.brand} {t.tire.model} {t.tire.size}",
            t.quantity,
            f"{t.unit_price:.2f}",
            f"{t.total_amount:.2f}",
            t.supplier.name if t.supplier else 'N/A',
            t.notes or ''
        ])
    output = si.getvalue()
    return Response(output, mimetype="text/csv", headers={"Content-Disposition":"attachment;filename=transactions.csv"})

@dashboard_bp.route('/export/reports')
@login_required
def export_reports():
    if not current_user.is_admin:
        return "Unauthorized", 403
    # Example: export monthly profit/loss report as CSV
    monthly_data = db.session.query(
        func.strftime('%Y-%m', Transaction.date),
        func.sum(
            func.case([
                (Transaction.transaction_type == 'sale', Transaction.total_amount),
                (Transaction.transaction_type == 'purchase', -Transaction.total_amount)
            ], else_=0)
        )
    ).group_by(
        func.strftime('%Y-%m', Transaction.date)
    ).all()
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['Month', 'Profit/Loss'])
    for month, profit_loss in monthly_data:
        cw.writerow([month, f"{profit_loss:.2f}"])
    output = si.getvalue()
    return Response(output, mimetype="text/csv", headers={"Content-Disposition":"attachment;filename=reports.csv"})

@dashboard_bp.route('/inventory')
@login_required
def inventory():
    tire_search = request.args.get('tire', '').strip()
    supplier_search = request.args.get('supplier', '').strip()
    min_quantity = request.args.get('min_quantity', '').strip()
    max_quantity = request.args.get('max_quantity', '').strip()

    query = Tire.query

    if tire_search:
        query = query.filter(
            (Tire.brand.ilike(f'%{tire_search}%')) |
            (Tire.model.ilike(f'%{tire_search}%')) |
            (Tire.size.ilike(f'%{tire_search}%'))
        )
    if supplier_search:
        query = query.join(Supplier).filter(Supplier.name.ilike(f'%{supplier_search}%'))
    if min_quantity.isdigit():
        query = query.filter(Tire.quantity >= int(min_quantity))
    if max_quantity.isdigit():
        query = query.filter(Tire.quantity <= int(max_quantity))

    tires = query.order_by(Tire.brand, Tire.model).all()
    reorder_tires = Tire.query.filter(Tire.quantity < Tire.min_stock).all()
    return render_template('dashboard/inventory.html', tires=tires, reorder_tires=reorder_tires)

@dashboard_bp.route('/transactions')
@login_required
def transactions():
    tire_search = request.args.get('tire', '').strip()
    supplier_search = request.args.get('supplier', '').strip()
    date_from = request.args.get('date_from', '').strip()
    date_to = request.args.get('date_to', '').strip()

    query = Transaction.query

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

    transactions = query.order_by(Transaction.date.desc()).all()
    return render_template('dashboard/transactions.html', transactions=transactions)

@dashboard_bp.route('/auto_reorder', methods=['POST'])
@login_required
def auto_reorder():
    if not current_user.is_admin:
        return "Unauthorized", 403
    reorder_tires = Tire.query.filter(Tire.quantity < Tire.min_stock).all()
    if not reorder_tires:
        flash('No tires need reordering.', 'info')
        return redirect(url_for('dashboard.inventory'))
    # Create purchase orders for reorder tires (simplified example)
    for tire in reorder_tires:
        # Here you would create purchase order entries or send notifications
        # For now, just log the reorder action
        print(f"Reorder triggered for tire {tire.brand} {tire.model} (ID: {tire.id})")
    flash(f'Automated reorder process triggered for {len(reorder_tires)} tires.', 'success')
    return redirect(url_for('dashboard.inventory'))

@dashboard_bp.route('/transactions')
@login_required
def transactions():
    transactions = Transaction.query.order_by(Transaction.date.desc()).all()
    return render_template('dashboard/transactions.html', transactions=transactions)

@dashboard_bp.route('/reports')
@login_required
def reports():
    # Monthly profit/loss calculation
    monthly_data = db.session.query(
        func.strftime('%Y-%m', Transaction.date),
        func.sum(
            case([
                (Transaction.transaction_type == 'sale', Transaction.total_amount),
                (Transaction.transaction_type == 'purchase', -Transaction.total_amount)
            ])
        )
    ).group_by(
        func.strftime('%Y-%m', Transaction.date)
    ).all()

    # Top selling tires
    top_selling = db.session.query(
        Tire.brand,
        Tire.model,
        Tire.size,
        func.count(Transaction.id).label('sales_count'),
        func.sum(Transaction.total_amount).label('total_sales')
    ).join(Transaction).filter(
        Transaction.transaction_type == 'sale'
    ).group_by(
        Tire.id
    ).order_by(
        func.sum(Transaction.total_amount).desc()
    ).limit(5).all()

    # Recent expenses
    recent_expenses = Expense.query.order_by(Expense.date.desc()).limit(5).all()
    
    return render_template('dashboard/reports.html', monthly_data=monthly_data, top_selling=top_selling, recent_expenses=recent_expenses)

# Expense API Endpoints
@dashboard_bp.route('/api/expenses', methods=['GET'])
@login_required
def get_expenses():
    try:
        expenses = Expense.query.order_by(Expense.date.desc()).all()
        return jsonify([{
            'id': e.id,
            'amount': e.amount,
            'category': e.category.value,
            'payment_method': e.payment_method.value,
            'description': e.description,
            'date': e.date.isoformat(),
            'receipt_number': e.receipt_number,
            'user_id': e.user_id
        } for e in expenses]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/api/expenses/<int:id>', methods=['GET'])
@login_required
def get_expense(id):
    try:
        expense = Expense.query.get_or_404(id)
        return jsonify({
            'id': expense.id,
            'amount': expense.amount,
            'category': expense.category.value,
            'payment_method': expense.payment_method.value,
            'description': expense.description,
            'date': expense.date.isoformat(),
            'receipt_number': expense.receipt_number,
            'user_id': expense.user_id
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/api/expenses', methods=['POST'])
@login_required
def create_expense():
    try:
        data = request.get_json()
        expense = Expense(
            amount=data['amount'],
            category=data['category'],
            payment_method=data['payment_method'],
            description=data.get('description', ''),
            date=datetime.fromisoformat(data['date']),
            receipt_number=data.get('receipt_number', ''),
            user_id=current_user.id
        )
        db.session.add(expense)
        db.session.commit()
        return jsonify({'message': 'Expense created successfully', 'id': expense.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@dashboard_bp.route('/api/expenses/<int:id>', methods=['PUT'])
@login_required
def update_expense(id):
    try:
        expense = Expense.query.get_or_404(id)
        data = request.get_json()
        
        expense.amount = data['amount']
        expense.category = data['category']
        expense.payment_method = data['payment_method']
        expense.description = data.get('description', expense.description)
        expense.date = datetime.fromisoformat(data['date'])
        expense.receipt_number = data.get('receipt_number', expense.receipt_number)
        
        db.session.commit()
        return jsonify({'message': 'Expense updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@dashboard_bp.route('/api/expenses/<int:id>', methods=['DELETE'])
@login_required
def delete_expense(id):
    try:
        expense = Expense.query.get_or_404(id)
        db.session.delete(expense)
        db.session.commit()
        return jsonify({'message': 'Expense deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
