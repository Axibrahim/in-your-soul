from flask import Blueprint, render_template, request, jsonify, session
from app.models import Product, Category, db
from datetime import datetime

main_bp = Blueprint('main', __name__)




@main_bp.route('/')
def index():
    cancel_expired_orders()  # Cancel expired orders before rendering the homepage
    featured = Product.query.filter_by(is_featured=True, is_active=True).limit(6).all()
    all_products = Product.query.filter_by(is_active=True).order_by(Product.created_at.desc()).limit(12).all()
    categories = Category.query.all()
    return render_template('main/index.html',
                           featured=featured,
                           products=all_products,
                           categories=categories)


@main_bp.route('/shop')
def shop():
    page = request.args.get('page', 1, type=int)
    category_slug = request.args.get('category', None)
    sort = request.args.get('sort', 'new')
    search = request.args.get('q', None)

    query = Product.query.filter_by(is_active=True)

    if category_slug:
        cat = Category.query.filter_by(slug=category_slug).first()
        if cat:
            query = query.filter_by(category_id=cat.id)

    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))

    if sort == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort == 'price_desc':
        query = query.order_by(Product.price.desc())
    else:
        query = query.order_by(Product.created_at.desc())

    products = query.paginate(page=page, per_page=12, error_out=False)
    categories = Category.query.all()

    return render_template('main/shop.html',
                           products=products,
                           categories=categories,
                           current_category=category_slug,
                           sort=sort,
                           search=search)


@main_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    related = Product.query.filter_by(
        category_id=product.category_id,
        is_active=True
    ).filter(Product.id != product_id).limit(4).all()
    return render_template('main/product_detail.html', product=product, related=related)


@main_bp.route('/about')
def about():
    return render_template('main/about.html')


@main_bp.route('/api/products')
def api_products():
    products = Product.query.filter_by(is_active=True).all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'price': p.price,
        'image_url': p.image_url,
        'stock': p.get_total_stock()
    } for p in products])



def cancel_expired_orders():
    from app.models import Order, ProductVariant
    expired = Order.query.filter(
        Order.payment_method.in_(['vodafone_cash', 'instapay']),
        Order.payment_status == 'unpaid',
        Order.status == 'pending',
        Order.payment_deadline < datetime.utcnow()
    ).all()
    for order in expired:
        order.status = 'cancelled'
        for item in order.items:
            variant = ProductVariant.query.get(item.variant_id)
            if variant:
                variant.stock += item.quantity
    if expired:
        db.session.commit()