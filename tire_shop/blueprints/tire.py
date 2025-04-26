from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from ..services.tire_service import TireService
from .forms import TireForm
from ..models import Tire

tire_bp = Blueprint('tire', __name__, url_prefix='/tires')

@tire_bp.route('/')
@login_required
def index():
    tires = TireService.get_all_tires()
    return render_template('tire/index.html', tires=tires)

@tire_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    form = TireForm()
    if form.validate_on_submit():
        data = {
            'brand': form.brand.data,
            'model': form.model.data,
            'size': form.size.data,
            'width': form.width.data,
            'aspect_ratio': form.aspect_ratio.data,
            'diameter': form.diameter.data,
            'load_index': form.load_index.data,
            'speed_rating': form.speed_rating.data,
            'season': form.season.data,
            'quantity': form.quantity.data,
            'purchase_price': form.purchase_price.data,
            'selling_price': form.selling_price.data,
            'min_stock': form.min_stock.data,
            'supplier_id': form.supplier.data.id if form.supplier.data else None
        }
        try:
            TireService.create_tire(data)
            flash('Tire created successfully.', 'success')
            return redirect(url_for('tire.index'))
        except Exception as e:
            flash(f'Error creating tire: {str(e)}', 'danger')
    return render_template('tire/form.html', form=form)

@tire_bp.route('/<int:tire_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(tire_id):
    tire = TireService.get_tire(tire_id)
    form = TireForm(obj=tire)
    if form.validate_on_submit():
        data = {
            'brand': form.brand.data,
            'model': form.model.data,
            'size': form.size.data,
            'width': form.width.data,
            'aspect_ratio': form.aspect_ratio.data,
            'diameter': form.diameter.data,
            'load_index': form.load_index.data,
            'speed_rating': form.speed_rating.data,
            'season': form.season.data,
            'quantity': form.quantity.data,
            'purchase_price': form.purchase_price.data,
            'selling_price': form.selling_price.data,
            'min_stock': form.min_stock.data,
            'supplier_id': form.supplier.data.id if form.supplier.data else None
        }
        try:
            TireService.update_tire(tire_id, data)
            flash('Tire updated successfully.', 'success')
            return redirect(url_for('tire.index'))
        except Exception as e:
            flash(f'Error updating tire: {str(e)}', 'danger')
    return render_template('tire/form.html', form=form, tire=tire)

@tire_bp.route('/<int:tire_id>/delete', methods=['POST'])
@login_required
def delete(tire_id):
    try:
        TireService.delete_tire(tire_id)
        flash('Tire deleted successfully.', 'success')
    except Exception as e:
        flash(f'Error deleting tire: {str(e)}', 'danger')
    return redirect(url_for('tire.index'))

@tire_bp.route('/<int:tire_id>')
@login_required
def view(tire_id):
    tire = TireService.get_tire(tire_id)
    return render_template('tire/view.html', tire=tire)