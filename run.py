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
    app.run(debug=True, host='0.0.0.0', port=5000)
