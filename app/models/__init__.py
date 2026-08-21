from app import db, login_manager, bcrypt
from flask_login import UserMixin
from datetime import datetime, timedelta
import json


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120), unique=True, nullable=True)
    email_verified = db.Column(db.Boolean, default=False, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    session_token = db.Column(db.String(64), nullable=True)
    session_issued_at = db.Column(db.DateTime, nullable=True)

    addresses = db.relationship('Address', backref='user', lazy=True, cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Address(db.Model):
    __tablename__ = 'addresses'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    label = db.Column(db.String(50), default='Home')
    street = db.Column(db.String(200), nullable=False)
    district = db.Column(db.String(100), nullable=False)
    governorate = db.Column(db.String(100), nullable=False)
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Address {self.label} - {self.governorate}>'


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    slug = db.Column(db.String(100), nullable=False, unique=True)
    products = db.relationship('Product', backref='category', lazy=True)


class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    image_url = db.Column(db.String(300))
    image_url_2 = db.Column(db.String(300))
    is_featured = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    variants = db.relationship('ProductVariant', backref='product', lazy=True, cascade='all, delete-orphan')
    order_items = db.relationship('OrderItem', backref='product', lazy=True)

    def get_total_stock(self):
        return sum(v.stock for v in self.variants)

    def __repr__(self):
        return f'<Product {self.name}>'


class ProductVariant(db.Model):
    __tablename__ = 'product_variants'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    size = db.Column(db.String(10), nullable=False)  # XS, S, M, L, XL, XXL
    stock = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<Variant {self.size}: {self.stock}>'


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, confirmed, shipped, delivered, cancelled
    payment_method = db.Column(db.String(50), nullable=False)  # cod, vodafone_cash, instapay
    payment_deadline = db.Column(db.DateTime, nullable=True)
    payment_status = db.Column(db.String(50), default='unpaid')
    subtotal = db.Column(db.Float, default=0)
    shipping_cost = db.Column(db.Float, default=0)
    total = db.Column(db.Float, default=0)
    shipping_address = db.Column(db.Text)  # JSON string of address
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

    def get_shipping_address(self):
        try:
            return json.loads(self.shipping_address) if self.shipping_address else {}
        except:
            return {}

    def set_shipping_address(self, addr_dict):
        self.shipping_address = json.dumps(addr_dict)

    @staticmethod
    def generate_order_number():
        import random, string
        return 'FRK-' + ''.join(random.choices(string.digits, k=8))

    def __repr__(self):
        return f'<Order {self.order_number}>'


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    variant_id = db.Column(db.Integer, db.ForeignKey('product_variants.id'))
    product_name = db.Column(db.String(200))
    size = db.Column(db.String(10))
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Float)
    total_price = db.Column(db.Float)

    variant = db.relationship('ProductVariant', backref='order_items')

    def __repr__(self):
        return f'<OrderItem {self.product_name} x{self.quantity}>'