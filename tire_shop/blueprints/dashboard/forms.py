from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SelectField, DateField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from wtforms_sqlalchemy.fields import QuerySelectField
from ..models import Tire, Supplier

def supplier_choices():
    return Supplier.query

class TireForm(FlaskForm):
    brand = StringField('Brand', validators=[DataRequired()])
    model = StringField('Model', validators=[DataRequired()])
    size = StringField('Size (e.g. 205/55R16)', validators=[DataRequired()])
    width = IntegerField('Width (mm)', validators=[DataRequired(), NumberRange(min=100, max=400)])
    aspect_ratio = IntegerField('Aspect Ratio', validators=[DataRequired(), NumberRange(min=30, max=100)])
    diameter = IntegerField('Diameter (inches)', validators=[DataRequired(), NumberRange(min=10, max=30)])
    load_index = StringField('Load Index')
    speed_rating = StringField('Speed Rating')
    season = SelectField('Season', choices=[
        ('summer', 'Summer'),
        ('winter', 'Winter'), 
        ('all-season', 'All Season')
    ])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=0)])
    purchase_price = FloatField('Purchase Price', validators=[DataRequired(), NumberRange(min=0)])
    selling_price = FloatField('Selling Price', validators=[DataRequired(), NumberRange(min=0)])
    min_stock = IntegerField('Minimum Stock', validators=[DataRequired(), NumberRange(min=0)])
    supplier = QuerySelectField('Supplier', query_factory=supplier_choices, get_label='name')
    submit = SubmitField('Save')

class TransactionForm(FlaskForm):
    transaction_type = SelectField('Type', choices=[
        ('purchase', 'Purchase'),
        ('sale', 'Sale')
    ], validators=[DataRequired()])
    tire = QuerySelectField('Tire', query_factory=lambda: Tire.query, get_label=lambda t: f"{t.brand} {t.model} {t.size}")
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    unit_price = FloatField('Unit Price', validators=[DataRequired(), NumberRange(min=0)])
    date = DateField('Date', validators=[DataRequired()])
    notes = TextAreaField('Notes')
    submit = SubmitField('Save')

class ExpenseForm(FlaskForm):
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0)])
    category = SelectField('Category', choices=[
        ('rent', 'Rent'),
        ('utilities', 'Utilities'),
        ('salaries', 'Salaries'),
        ('maintenance', 'Maintenance'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    payment_method = SelectField('Payment Method', choices=[
        ('cash', 'Cash'),
        ('check', 'Check'),
        ('card', 'Card'),
        ('transfer', 'Transfer')
    ], validators=[DataRequired()])
    description = TextAreaField('Description')
    date = DateField('Date', validators=[DataRequired()])
    receipt_number = StringField('Receipt Number')
    submit = SubmitField('Save')