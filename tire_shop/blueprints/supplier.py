from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from wtforms import Form, StringField, TextAreaField, validators
from ..models import Supplier
from ..services.supplier_service import SupplierService
from .. import db

supplier_bp = Blueprint('supplier', __name__, url_prefix='/suppliers')

class SupplierForm(Form):
    name = StringField('Nom', [validators.DataRequired(), validators.Length(max=120)])
    contact_person = StringField('Personne de contact', [validators.Optional(), validators.Length(max=80)])
    phone = StringField('Téléphone', [validators.Optional(), validators.Length(max=20)])
    email = StringField('Email', [validators.Optional(), validators.Email(), validators.Length(max=120)])
    address = TextAreaField('Adresse', [validators.Optional()])
    tax_id = StringField('Identifiant fiscal', [validators.Optional(), validators.Length(max=50)])
    payment_terms = StringField('Conditions de paiement', [validators.Optional(), validators.Length(max=100)])
    notes = TextAreaField('Notes', [validators.Optional()])

@supplier_bp.route('/')
@login_required
def index():
    suppliers = SupplierService.get_all_suppliers()
    return render_template('suppliers/index.html', suppliers=suppliers)

@supplier_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    form = SupplierForm(request.form)
    if request.method == 'POST' and form.validate():
        data = {
            'name': form.name.data,
            'contact_person': form.contact_person.data,
            'phone': form.phone.data,
            'email': form.email.data,
            'address': form.address.data,
            'tax_id': form.tax_id.data,
            'payment_terms': form.payment_terms.data,
            'notes': form.notes.data
        }
        try:
            SupplierService.create_supplier(data)
            flash('Fournisseur créé avec succès.', 'success')
            return redirect(url_for('supplier.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la création du fournisseur : {str(e)}', 'danger')
    return render_template('suppliers/form.html', form=form)

@supplier_bp.route('/<int:supplier_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(supplier_id):
    supplier = SupplierService.get_supplier(supplier_id)
    form = SupplierForm(request.form, obj=supplier)
    if request.method == 'POST' and form.validate():
        data = {
            'name': form.name.data,
            'contact_person': form.contact_person.data,
            'phone': form.phone.data,
            'email': form.email.data,
            'address': form.address.data,
            'tax_id': form.tax_id.data,
            'payment_terms': form.payment_terms.data,
            'notes': form.notes.data
        }
        try:
            SupplierService.update_supplier(supplier_id, data)
            flash('Fournisseur mis à jour avec succès.', 'success')
            return redirect(url_for('supplier.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la mise à jour du fournisseur : {str(e)}', 'danger')
    return render_template('suppliers/form.html', form=form, supplier=supplier)

@supplier_bp.route('/<int:supplier_id>')
@login_required
def view(supplier_id):
    supplier = SupplierService.get_supplier(supplier_id)
    return render_template('suppliers/view.html', supplier=supplier)

@supplier_bp.route('/<int:supplier_id>/delete', methods=['POST'])
@login_required
def delete(supplier_id):
    try:
        SupplierService.delete_supplier(supplier_id)
        flash('Fournisseur supprimé avec succès.', 'success')
    except Exception as e:
        flash(f'Erreur lors de la suppression du fournisseur : {str(e)}', 'danger')
    return redirect(url_for('supplier.index'))