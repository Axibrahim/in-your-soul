
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app.models import OrderItem, Product, ProductVariant, Category, Order, User, db
from functools import wraps
import os, re, time, secrets
from werkzeug.utils import secure_filename
from PIL import Image
from supabase import create_client, Client

admin_bp = Blueprint('admin', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
ALLOWED_PIL_FORMATS = {'PNG', 'JPEG', 'WEBP', 'GIF'}

# Initialize Supabase Client
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None
BUCKET_NAME = "product-images"


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Access denied. Admin only.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')


def save_product_image(file):
    if not file or not file.filename or not allowed_file(file.filename):
        return None

    try:
        image = Image.open(file.stream)
        image.verify()
        file.stream.seek(0)
        image = Image.open(file.stream)
        image_format = image.format
    except Exception:
        current_app.logger.warning("Image validation failed for %s", file.filename)
        return None

    if image_format not in ALLOWED_PIL_FORMATS:
        return None

    base = secure_filename(os.path.splitext(file.filename)[0]) or 'image'
    ext = image_format.lower().replace('jpeg', 'jpg')
    filename = f"{base}_{int(time.time())}_{secrets.token_hex(4)}.{ext}"

    content_type_map = {'jpg': 'image/jpeg', 'png': 'image/png', 'webp': 'image/webp', 'gif': 'image/gif'}
    content_type = content_type_map.get(ext, file.content_type or 'application/octet-stream')

    if not supabase:
        current_app.logger.error("Supabase client not configured — check SUPABASE_URL / SUPABASE_KEY env vars")
        return None

    try:
        file.stream.seek(0)
        file_bytes = file.stream.read()

        supabase.storage.from_(BUCKET_NAME).upload(
            path=filename,
            file=file_bytes,
            file_options={"content-type": content_type, "upsert": "true"}
        )
        return supabase.storage.from_(BUCKET_NAME).get_public_url(filename)
    except Exception as e:
        current_app.logger.exception("Supabase upload failed for %s: %s", filename, e)
        return None

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    total_orders = Order.query.count()
    pending_orders = Order.query.filter_by(status='pending').count()
    total_products = Product.query.filter_by(is_active=True).count()
    total_users = User.query.count()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    revenue = db.session.query(db.func.sum(Order.total)).filter(
        Order.status.in_(['confirmed', 'shipped', 'delivered'])
    ).scalar() or 0

    return render_template('admin/dashboard.html',
                           total_orders=total_orders,
                           pending_orders=pending_orders,
                           total_products=total_products,
                           total_users=total_users,
                           recent_orders=recent_orders,
                           revenue=revenue)


@admin_bp.route('/products')
@login_required
@admin_required
def products():
    products = Product.query.order_by(Product.created_at.desc()).all()
    return render_template('admin/products.html', products=products)


@admin_bp.route('/products/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product():
    categories = Category.query.all()
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        price = request.form.get('price', type=float)
        category_id = request.form.get('category_id', type=int)
        is_featured = request.form.get('is_featured') == 'on'

        if not name or not price:
            flash('Name and price are required.', 'danger')
            return render_template('admin/add_product.html', categories=categories)

        product = Product(
            name=name,
            description=description,
            price=price,
            category_id=category_id,
            is_featured=is_featured
        )

        for field_name, attr in [('image', 'image_url'), ('image2', 'image_url_2')]:
            file = request.files.get(field_name)
            public_url = save_product_image(file)
            if public_url:
                setattr(product, attr, public_url)
            elif file and file.filename:
                flash(f'{field_name}: file was not a valid image or upload failed and was skipped.', 'danger')

        db.session.add(product)
        db.session.flush()

        sizes = ['M', 'L', 'XL']
        for size in sizes:
            stock = request.form.get(f'stock_{size}', 0, type=int)
            if stock >= 0:
                variant = ProductVariant(product_id=product.id, size=size, stock=stock)
                db.session.add(variant)

        db.session.commit()
        flash(f'Product "{name}" added successfully.', 'success')
        return redirect(url_for('admin.products'))

    return render_template('admin/add_product.html', categories=categories)


@admin_bp.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    categories = Category.query.all()

    if request.method == 'POST':
        product.name = request.form.get('name', '').strip()
        product.description = request.form.get('description', '').strip()
        product.price = request.form.get('price', type=float)
        product.category_id = request.form.get('category_id', type=int)
        product.is_featured = request.form.get('is_featured') == 'on'
        product.is_active = request.form.get('is_active') == 'on'

        for field_name, attr in [('image', 'image_url'), ('image2', 'image_url_2')]:
            file = request.files.get(field_name)
            public_url = save_product_image(file)
            if public_url:
                setattr(product, attr, public_url)
            elif file and file.filename:
                flash(
                    f'{field_name}: file was not a valid image or upload failed and was skipped.',
                    'danger'
                )

        # Default sizes: M, L, XL
        for size in ['M', 'L', 'XL']:
            stock = request.form.get(f'stock_{size}', 0, type=int)

            variant = ProductVariant.query.filter_by(
                product_id=product.id,
                size=size
            ).first()

            if variant:
                variant.stock = max(0, stock)
            else:
                db.session.add(
                    ProductVariant(
                        product_id=product.id,
                        size=size,
                        stock=max(0, stock)
                    )
                )

        # Optional sizes: XS, S, XXL, XXXL
        for size in ['XS', 'S', 'XXL', 'XXXL']:
            variant = ProductVariant.query.filter_by(
                product_id=product.id,
                size=size
            ).first()

            enabled = request.form.get(f'enable_{size}') == 'on'

            if enabled:
                stock = request.form.get(f'stock_{size}', 0, type=int)

                if variant:
                    variant.stock = max(0, stock)
                else:
                    db.session.add(
                        ProductVariant(
                            product_id=product.id,
                            size=size,
                            stock=max(0, stock)
                        )
                    )

            elif variant:
                # Hide optional size without deleting the variant
                variant.stock = 0

        db.session.commit()
        flash('Product updated.', 'success')
        return redirect(url_for('admin.products'))

    return render_template(
        'admin/edit_product.html',
        product=product,
        categories=categories
    )


@admin_bp.route('/products/<int:product_id>/deactivate', methods=['POST'])
@login_required
@admin_required
def deactivate_product(product_id):
    product = Product.query.get_or_404(product_id)

    product.is_active = False
    db.session.commit()

    flash(f'Product "{product.name}" deactivated.', 'success')
    return redirect(url_for('admin.products'))


@admin_bp.route('/products/<int:product_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)

    # Do not permanently delete products that are already part of orders
    if OrderItem.query.filter_by(product_id=product.id).first():
        flash(
            'This product cannot be permanently deleted because it is linked to existing orders. '
            'Deactivate it instead.',
            'danger'
        )
        return redirect(url_for('admin.products'))

    # Delete product variants first
    ProductVariant.query.filter_by(product_id=product.id).delete(
        synchronize_session=False
    )

    # Delete the product
    db.session.delete(product)
    db.session.commit()

    flash(f'Product "{product.name}" permanently deleted.', 'success')
    return redirect(url_for('admin.products'))

@admin_bp.route('/products/<int:product_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_product(product_id):
    product = Product.query.get_or_404(product_id)
    product.is_active = not product.is_active
    db.session.commit()
    return jsonify({'success': True, 'is_active': product.is_active})


@admin_bp.route('/orders')
@login_required
@admin_required
def orders():
    status_filter = request.args.get('status', None)
    query = Order.query.order_by(Order.created_at.desc())
    if status_filter:
        query = query.filter_by(status=status_filter)
    orders = query.all()
    return render_template('admin/orders.html', orders=orders, status_filter=status_filter)


@admin_bp.route('/orders/<int:order_id>')
@login_required
@admin_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('admin/order_detail.html', order=order)


@admin_bp.route('/orders/<int:order_id>/status', methods=['POST'])
@login_required
@admin_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    valid = ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']
    if new_status in valid:
        order.status = new_status
        db.session.commit()
        flash(f'Order status updated to {new_status}.', 'success')
    return redirect(url_for('admin.order_detail', order_id=order_id))


@admin_bp.route('/categories')
@login_required
@admin_required
def categories():
    cats = Category.query.all()
    return render_template('admin/categories.html', categories=cats)


@admin_bp.route('/categories/add', methods=['POST'])
@login_required
@admin_required
def add_category():
    name = request.form.get('name', '').strip()
    if name:
        slug = slugify(name)
        if not Category.query.filter_by(slug=slug).first():
            cat = Category(name=name, slug=slug)
            db.session.add(cat)
            db.session.commit()
            flash(f'Category "{name}" added.', 'success')
        else:
            flash('Category already exists.', 'danger')
    return redirect(url_for('admin.categories'))


@admin_bp.route('/categories/<int:cat_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_category(cat_id):
    cat = Category.query.get_or_404(cat_id)
    db.session.delete(cat)
    db.session.commit()
    flash('Category deleted.', 'success')
    return redirect(url_for('admin.categories'))


@admin_bp.route('/users')
@login_required
@admin_required
def users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)


@admin_bp.route('/users/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user.id != current_user.id:
        user.is_admin = not user.is_admin
        db.session.commit()
    return jsonify({'success': True, 'is_admin': user.is_admin})
