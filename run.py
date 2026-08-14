import os
from app import create_app, db
from app.models import User, Product, Category, ProductVariant, Order, OrderItem, Address

app = create_app('development')

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Product': Product,
        'Category': Category,
        'ProductVariant': ProductVariant,
        'Order': Order,
        'OrderItem': OrderItem,
        'Address': Address,
    }



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username="bahz").first():
            import secrets
            bootstrap_password = os.environ.get("ADMIN_BOOTSTRAP_PASSWORD") or secrets.token_urlsafe(12)
            admin = User(first_name="Amr", last_name="Ibrahim", username="bahz", is_admin=True)
            admin.set_password(bootstrap_password)
            db.session.add(admin)
            db.session.commit()
            print(f"Admin account created. Password: {bootstrap_password}  (change it immediately)")
    app.run(debug=(os.environ.get("FLASK_ENV") != "production"), host='0.0.0.0', port=5000)